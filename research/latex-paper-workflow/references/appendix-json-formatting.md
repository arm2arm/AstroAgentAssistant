Appendix JSON formatting — options to avoid Overfull \hbox from long unbroken JSON blocks

When papers include long, machine-generated JSON blocks (DRP cards, provenance manifests), they routinely produce Overfull \hbox warnings and broken layout in journal templates. This note summarizes practical approaches used successfully in recent sessions.

1) Enable breakable verbatim with fvextra + fancyvrb
- Add to preamble:
  \usepackage{fvextra}
  \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,fontsize=\small}
- Replace \begin{verbatim} ... \end{verbatim} with \begin{Highlighting} ... \end{Highlighting}
- Pros: preserves text, machine-readable, minimal effort
- Cons: may still overflow margins in some journal classes; line breaks are generic (mid-token sometimes)

2) Use listings with breaklines and basic styling
- Preamble additions:
  \usepackage{listings}
  \lstset{basicstyle=\ttfamily\small,breaklines=true,breakatwhitespace=false}
- Wrap JSON in:\begin{lstlisting} ... \end{lstlisting}
- Pros: more control over styling and language highlight, works well with long lines
- Cons: no JSON-specific highlighting without external packages; minted provides color but needs Pygments and -shell-escape

3) Use minted (Pygments) for high-quality JSON highlighting (requires shell-escape)
- Preamble additions:
  \usepackage{minted}
- Compile with: pdflatex -shell-escape -interaction=nonstopmode main-webofc.tex
- Use: \begin{minted}[breaklines,fontsize=\small]{json} ... \end{minted}
- Pros: nicest look, JSON-aware formatting
- Cons: requires Pygments and -shell-escape; not allowed on some CI / journal submission systems

4) Convert JSON to an image (PNG) programmatically
- Use a short Python rendering script that pretty-prints JSON and renders in a monospace box, then save as PNG. Example:

  python3 - <<'PY'
  import json, sys
  from PIL import Image, ImageFont, ImageDraw
  j = json.load(open('example.json'))
  s = json.dumps(j, indent=2)
  font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 12)
  lines = s.splitlines()
  w = max(font.getsize(line)[0] for line in lines)+20
  h = (len(lines)+1)*(font.getsize('A')[1]+2)+20
  img = Image.new('RGB',(w,h),'white')
  draw = ImageDraw.Draw(img)
  y=10
  for line in lines:
      draw.text((10,y), line, font=font, fill='black')
      y += font.getsize(line)[1]+2
  img.save('example_json.png')
PY

- Include in LaTeX with \includegraphics[width=\textwidth]{example_json.png}
- Pros: preserves exact formatting and layout, safe for journals that disallow -shell-escape
- Cons: not machine-readable in the PDF, increases repository size, needs careful DPI/quality selection

5) Use small-font multi-column presentation in appendices
- For extremely long JSONs consider a two-column, \scriptsize environment inside the appendix. This often reduces overfulls but is less readable.

6) Practical recommendation (default):
- Prefer listings with breaklines or fvextra if shell-escape is unacceptable. Use minted only when you control the build environment and can run -shell-escape. Convert to image only for final submission if the journal complains about layout.

7) Example LaTeX snippet (listings):

\usepackage{listings}
\lstset{basicstyle=\ttfamily\small,breaklines=true,breakatwhitespace=false}

\begin{lstlisting}[language=json]
{"actor": "hermes", "action": "prepared Zenodo release and DRP-Hub registration", "timestamp": "2026-06-04T09:45:00Z", "doi": "10.5281/zenodo.1234567", "human_reviewed": true}
\end{lstlisting}

8) Adding to the skill
- This file is saved under the latex-paper-workflow skill references directory. The main SKILL.md includes a pointer.
- When the user requests appendix layout fixes, use this file to pick the default approach and implement it across the project.
