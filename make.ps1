param([ValidateSet('install','run','plot','real','real-basemap','real-atalaia-nome','real-atalaia-bbox','test','slides','slides-notes','gamma-visual','gamma-card','clean')][string]$task='run')

switch ($task) {
  'install' {
    pip install -r requirements.txt
  }

  'run' {
    $env:PYTHONPATH = 'src'
    python -m pcc.solve_cli --input data\example_edges.csv
  }

  'plot' {
    if (-not (Test-Path out)) { New-Item -ItemType Directory -Path out | Out-Null }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    $env:PYTHONPATH = 'src'
    python -m pcc.solve_cli --input data\example_edges.csv --plot `
      --label-mode all --edge-labels --show-start `
      --node-size 620 --label-size 12 --edge-alpha 0.40 --edge-width 2.2 --dpi 280 `
      --save-plot out\example.png --save-tour out\example_tour.txt
    Copy-Item out\example.png slides\img\example.png -Force
  }

  'real' {
    if (-not (Test-Path out)) { New-Item -ItemType Directory -Path out | Out-Null }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    $bbox = "-37.0628,-10.9496,-37.0564,-10.9435"  # Bairro Jardins (Aracaju)
  python tools\geojson_to_csv.py data\osm_subgraph.geojson data\real_edges.csv --snap-m 12 --nodes-out data\real_nodes.csv --bbox="$bbox"
    $env:PYTHONPATH = 'src'
    python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
      --label-mode junctions --edge-labels --show-start --edge-alpha 0.32 --edge-width 2.9 --layout-k 1.0 --fig-width 12 --fig-height 9 --dpi 320 `
      --save-plot out\real_solution.png --save-tour out\real_tour.txt `
      --save-geojson out\real_tour.geojson --save-gpx out\real_tour.gpx
    Copy-Item out\real_solution.png slides\img\real_solution.png -Force
  }

  'real-basemap' {
    if (-not (Test-Path out)) { New-Item -ItemType Directory -Path out | Out-Null }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    $bbox = "-37.0628,-10.9496,-37.0564,-10.9435"  # Bairro Jardins (Aracaju)
  python tools\geojson_to_csv.py data\osm_subgraph.geojson data\real_edges.csv --snap-m 12 --nodes-out data\real_nodes.csv --bbox="$bbox"
    $env:PYTHONPATH = 'src'
    python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
  --style tour --basemap --basemap-provider CartoDB.Positron --basemap-zoom 17 `
      --label-mode junctions --edge-labels --show-start --edge-alpha 0.55 --edge-width 3.4 --fig-width 13 --fig-height 9.5 --dpi 320 `
      --save-plot out\real_solution_basemap.png --save-tour out\real_tour.txt `
      --save-geojson out\real_tour.geojson --save-gpx out\real_tour.gpx
    Copy-Item out\real_solution_basemap.png slides\img\real_solution_basemap.png -Force
  }

  'real-atalaia-nome' {
    if (-not (Test-Path out)) { New-Item -ItemType Directory -Path out | Out-Null }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    python tools\geojson_to_csv.py data\osm_subgraph.geojson data\atalaia_edges.csv --snap-m 10 `
      --nodes-out data\atalaia_nodes.csv --include-name-substr "Vinícius,João Carvalho,Concordia,Lions,Durval Maynard,Otávio Souza Leite"
    $env:PYTHONPATH = 'src'
    python -m pcc.solve_cli --input data\atalaia_edges.csv --nodes data\atalaia_nodes.csv --largest-component --plot `
      --label-mode junctions --edge-labels --show-start `
      --node-size 520 --label-size 11 --edge-alpha 0.45 --edge-width 2.6 --dpi 300 `
      --save-plot out\atalaia_tour.png --save-tour out\atalaia_tour.txt --save-geojson out\atalaia_tour.geojson --save-gpx out\atalaia_tour.gpx
    Copy-Item out\atalaia_tour.png slides\img\atalaia_tour.png -Force
  }

  'real-atalaia-bbox' {
    if (-not (Test-Path out)) { New-Item -ItemType Directory -Path out | Out-Null }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }

    # BBox alternativa na Atalaia (minlon,minlat,maxlon,maxlat) — ajuste conforme desejar
    $bbox = "-37.0608,-10.9968,-37.0545,-10.9918"

    # Converter GeoJSON -> CSV (arestas e nós)
    python tools\geojson_to_csv.py data\osm_subgraph.geojson data\atalaia_edges.csv --snap-m 10 `
      --nodes-out data\atalaia_nodes.csv --bbox $bbox

    # Resolver e gerar artefatos com rótulos e marcação do início/fim
    $env:PYTHONPATH = 'src'
    python -m pcc.solve_cli --input data\atalaia_edges.csv --nodes data\atalaia_nodes.csv --largest-component --plot `
      --label-mode junctions --edge-labels --show-start `
      --node-size 520 --label-size 11 --edge-alpha 0.45 --edge-width 2.6 --dpi 300 `
      --save-plot out\atalaia_tour.png --save-tour out\atalaia_tour.txt --save-geojson out\atalaia_tour.geojson --save-gpx out\atalaia_tour.gpx

    # Copiar para os slides
    Copy-Item out\atalaia_tour.png slides\img\atalaia_tour.png -Force
  }

  'test' {
    python -m pytest -q
  }

  'slides' {
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    if (-not (Test-Path out\example.png)) { & $PSCommandPath plot }
    if (-not (Test-Path out\real_solution.png) -and -not (Test-Path out\real_solution_basemap.png)) { & $PSCommandPath real }
    if (Test-Path out\real_solution.png) {
      Copy-Item out\real_solution.png slides\img\real_solution.png -Force
    }
    if (Test-Path out\real_solution_basemap.png) {
      Copy-Item out\real_solution_basemap.png slides\img\real_solution_basemap.png -Force
    } elseif (Test-Path out\real_solution.png) {
      Copy-Item out\real_solution.png slides\img\real_solution_basemap.png -Force
    }
    Copy-Item out\example.png slides\img\example.png -Force
    npx @marp-team/marp-cli slides\seminario.md -o slides\seminario.pdf --allow-local-files
  }

  'slides-notes' {
    if (-not (Test-Path slides\seminario_notes.md)) {
      Write-Host "Arquivo slides/seminario_notes.md não encontrado." -ForegroundColor Yellow
      break
    }
    npx @marp-team/marp-cli slides\seminario_notes.md -o slides\seminario_notes.pdf --allow-local-files
  }

  'gamma-visual' {
    if (-not (Test-Path out\real_solution.png)) {
      Write-Host "Gerando out/real_solution.png com tarefa 'real'..." -ForegroundColor Cyan
      & $PSCommandPath real
    }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    $env:PYTHONPATH = 'src'
    python tools\slide_visual_from_outputs.py --input data\real_edges.csv --nodes data\real_nodes.csv `
      --background out\real_solution.png --out slides\img\interpretando_saida.png
    if (Test-Path slides\img\interpretando_saida.png) {
      Write-Host "Visual para Gamma salvo em slides/img/interpretando_saida.png" -ForegroundColor Green
    }
  }

  'gamma-card' {
    if (-not (Test-Path out\real_solution.png)) {
      Write-Host "Gerando out/real_solution.png com tarefa 'real'..." -ForegroundColor Cyan
      & $PSCommandPath real
    }
    if (-not (Test-Path slides\img)) { New-Item -ItemType Directory -Path slides\img | Out-Null }
    $env:PYTHONPATH = 'src'
    python tools\real_card_visual.py --input data\real_edges.csv `
      --background out\real_solution.png --out slides\img\real_card.png --corner tr
    if (Test-Path slides\img\real_card.png) {
      Write-Host "Card compacto salvo em slides/img/real_card.png" -ForegroundColor Green
    }
  }

  'clean' {
    Remove-Item -Recurse -Force out 2>$null
    Remove-Item -Recurse -Force .pytest_cache 2>$null
  }

  default {
    Write-Host "Uso: .\make.ps1 [install|run|plot|real|real-basemap|real-atalaia-nome|real-atalaia-bbox|test|slides|slides-notes|gamma-visual|clean]" -ForegroundColor Yellow
  }
}