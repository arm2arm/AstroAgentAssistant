# Native Editable Charts in python-pptx

When the user asks for "editable diagrams/charts" in a .pptx, build **native PowerPoint
charts** (`shapes.add_chart`) — never matplotlib PNGs. Native charts survive re-editing,
data updates, and recoloring in PowerPoint. Pattern proven 2026-08-18 building a 3-slide
S3 storage benchmark deck (3 clustered bar charts + 1 native table, QA'd via LibreOffice).

## API gotchas (all hit in practice)

1. **`series.data_labels`, not `series.datalabels`** — `AttributeError: 'BarSeries' object
   has no attribute 'datalabels'. Did you mean: 'data_labels'?`
2. **`axis.major_tick_mark = None` raises** `ValueError: None is not a valid XL_TICK_MARK`.
   Import `XL_TICK_MARK` from `pptx.enum.chart` and set `XL_TICK_MARK.NONE`.
3. **Log scale has no API** — inject XML after setting min/max scale:
   ```python
   from pptx.oxml.ns import qn
   va = chart.value_axis
   va.minimum_scale, va.maximum_scale = 0.05, 300
   scaling = va._element.find(qn("c:scaling"))
   scaling.append(scaling.makeelement(qn("c:logBase"), {"val": "10"}))
   ```
4. **Data labels collide with x-axis category labels on log-scale charts** — the near-zero
   first bars get OUTSIDE_END labels that land on top of the category text. Fix: per-point
   labels that skip the tiny points (see `labels_skip_first` below), or drop chart labels
   and put exact values in a side table / callout pills.

## Working helpers

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import (XL_CHART_TYPE, XL_LEGEND_POSITION,
                             XL_LABEL_POSITION, XL_TICK_MARK)
from pptx.oxml.ns import qn

def set_series_color(chart, idx, rgb):
    ser = chart.series[idx]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb
    ser.format.line.fill.background()

def style_axis(chart, log=False, max_v=None, min_v=None):
    va = chart.value_axis
    va.format.line.color.rgb = BORDER
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    va.major_gridlines.format.line.width = Pt(0.75)
    va.tick_labels.font.size = Pt(10)
    va.tick_labels.font.color.rgb = MUT
    ca = chart.category_axis
    ca.tick_labels.font.size = Pt(10.5)
    ca.tick_labels.font.color.rgb = MUT
    if log:
        scaling = va._element.find(qn("c:scaling"))
        scaling.append(scaling.makeelement(qn("c:logBase"), {"val": "10"}))
    if max_v is not None: va.maximum_scale = max_v
    if min_v is not None: va.minimum_scale = min_v
    for ax in (va, ca):
        ax.major_tick_mark = XL_TICK_MARK.NONE
        ax.minor_tick_mark = XL_TICK_MARK.NONE

def add_data_labels(chart, fmt="0.0"):
    for ser in chart.series:
        dl = ser.data_labels          # NOT .datalabels
        dl.show_value = True
        dl.number_format = fmt
        dl.number_format_is_linked = False
        dl.font.size = Pt(10); dl.font.bold = True
        dl.font.color.rgb = INK
        dl.position = XL_LABEL_POSITION.OUTSIDE_END

def labels_skip_first(chart):
    """Per-point labels on points 1..n-1 only — skips the tiny first bar
    whose OUTSIDE_END label collides with x-axis category text on log scale.
    Replace idxs=(1,2) with the points you want labelled."""
    for ser in chart.series:
        el = ser._element
        for d in el.findall(qn("c:dLbls")):
            el.remove(d)
        dLbls = el.makeelement(qn("c:dLbls"), {})
        for idx in (1, 2):
            dLbl = dLbls.makeelement(qn("c:dLbl"), {})
            dLbl.append(dLbl.makeelement(qn("c:idx"), {"val": str(idx)}))
            txPr = dLbl.makeelement(qn("c:txPr"), {})
            p = txPr.makeelement(qn("a:p"), {})
            pPr = p.makeelement(qn("a:pPr"), {})
            defRPr = pPr.makeelement(qn("a:defRPr"), {"sz": "1000", "b": "1"})
            defRPr.append(defRPr.makeelement(qn("a:srgbClr"), {"val": "0F172A"}))
            pPr.append(defRPr); p.append(pPr)
            txPr.append(txPr.makeelement(qn("a:bodyPr"), {}))
            txPr.append(txPr.makeelement(qn("a:lstStyle"), {}))
            txPr.append(p)
            dLbl.append(txPr)
            dLbls.append(dLbl)
        dLbls.append(dLbls.makeelement(qn("c:showVal"), {"val": "1"}))
        for b in ("showCatName", "showSerName", "showPercent", "showBubbleSize"):
            dLbls.append(dLbls.makeelement(qn(f"c:{b}"), {"val": "0"}))
        cat = el.find(qn("c:cat"))
        (cat.addprevious(dLbls) if cat is not None else el.append(dLbls))
```

## Deck recipe (clustered columns)

```python
cd = CategoryChartData()
cd.categories = ["1 workers", "4 workers", "8 workers", "16 workers"]
cd.add_series("RustFS (9000)", tuple(rust_vals))
cd.add_series("VersityGW (7070)", tuple(versity_vals))
gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                            Inches(x), Inches(y), Inches(w), Inches(h), cd)
ch = gf.chart
ch.has_title = True
ch.chart_title.text_frame.text = "Parallel read throughput (MB/s)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(13)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False   # legend doesn't eat plot area
ch.legend.font.size = Pt(10.5)
set_series_color(ch, 0, BLUE); set_series_color(ch, 1, AMBER)
style_axis(ch, max_v=95)
add_data_labels(ch, fmt="0.0")
```

## Native table (editable) for exact values

```python
shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
tbl = shape.table
tbl.columns[i].width = Inches(...)
cell = tbl.cell(r, c)
cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.02)
cell.vertical_anchor = MSO_ANCHOR.MIDDLE
cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
p = cell.text_frame.paragraphs[0]; p.text = value
```

## Verify embedded chart data after build

Vision QA on low-res thumbnails misreads numbers — verify the actual embedded values:

```python
p = Presentation("out.pptx")
for s in p.slides:
    for sh in s.shapes:
        if sh.has_chart:
            for ser in sh.chart.series:
                print(ser.name, list(ser.values))
        if sh.has_table:
            print([c.text for c in sh.table.rows[0].cells])
```

## Layout notes

- Log-scale column charts: set `minimum_scale` ≥ ~0.05–0.2 so the smallest bar is visible
  but not a sub-pixel sliver; `maximum_scale` ~4× the largest value leaves headroom for labels.
- Pair log-scale charts with callout pills (rounded rects) carrying the headline numbers in
  linear context — pills read faster than log bars in a projector setting.
- Keep chart titles in the chart object (not external text boxes) so they move with the chart.
