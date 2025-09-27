.PHONY: install run plot real real-basemap real-atalaia-nome real-atalaia-bbox test slides clean

install:
    python -m pip install -r requirements.txt

run:
    PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv

plot:
    mkdir -p out slides/img
    PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --plot \
        --label-mode all --edge-labels --edge-alpha 0.40 --edge-width 2.2 --dpi 260 \
        --save-plot out/example.png --save-tour out/example_tour.txt
    cp -f out/example.png slides/img/example.png

real:
    mkdir -p out slides/img
    python tools/geojson_to_csv.py data/osm_subgraph.geojson data/real_edges.csv --snap-m 12 --nodes-out data/real_nodes.csv --bbox "-37.0628,-10.9496,-37.0564,-10.9435"
    PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
        --label-mode junctions --edge-labels --show-start --edge-alpha 0.32 --edge-width 2.9 --fig-width 12 --fig-height 9 --dpi 320 \
        --save-plot out/real_solution.png --save-tour out/real_tour.txt \
        --save-geojson out/real_tour.geojson --save-gpx out/real_tour.gpx
    cp -f out/real_solution.png slides/img/real_solution.png

real-basemap:
    mkdir -p out slides/img
    python tools/geojson_to_csv.py data/osm_subgraph.geojson data/real_edges.csv --snap-m 12 --nodes-out data/real_nodes.csv --bbox "-37.0628,-10.9496,-37.0564,-10.9435"
    PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
        --style tour --basemap --basemap-provider CartoDB.Positron --basemap-zoom 17 \
        --label-mode junctions --edge-labels --show-start --edge-alpha 0.55 --edge-width 3.4 --fig-width 13 --fig-height 9.5 --dpi 320 \
        --save-plot out/real_solution_basemap.png --save-tour out/real_tour.txt \
        --save-geojson out/real_tour.geojson --save-gpx out/real_tour.gpx
    cp -f out/real_solution_basemap.png slides/img/real_solution.png

real-atalaia-nome:
    mkdir -p out
    python tools/geojson_to_csv.py data/osm_subgraph.geojson data/atalaia_edges.csv --snap-m 10 \
        --nodes-out data/atalaia_nodes.csv --include-name-substr "Vinícius,João Carvalho,Concordia,Lions,Durval Maynard,Otávio Souza Leite"
    PYTHONPATH=src python -m pcc.solve_cli --input data/atalaia_edges.csv --nodes data/atalaia_nodes.csv --largest-component --plot \
        --label-mode junctions --edge-labels --edge-alpha 0.40 --edge-width 2.4 --dpi 260 \
        --save-plot out/atalaia_tour.png --save-tour out/atalaia_tour.txt --save-geojson out/atalaia_tour.geojson --save-gpx out/atalaia_tour.gpx

real-atalaia-bbox:
    mkdir -p out
    # BBox alternativa na Atalaia (ajuste as coordenadas)
    python tools/geojson_to_csv.py data/osm_subgraph.geojson data/atalaia_edges.csv --snap-m 10 \
        --nodes-out data/atalaia_nodes.csv --bbox "-37.0608,-10.9968,-37.0545,-10.9918"
    PYTHONPATH=src python -m pcc.solve_cli --input data/atalaia_edges.csv --nodes data/atalaia_nodes.csv --largest-component --plot \
        --label-mode junctions --edge-labels --edge-alpha 0.40 --edge-width 2.4 --dpi 260 \
        --save-plot out/atalaia_tour.png --save-tour out/atalaia_tour.txt --save-geojson out/atalaia_tour.geojson --save-gpx out/atalaia_tour.gpx

test:
    pytest -q

slides:
    npx @marp-team/marp-cli slides/seminario.md -o slides/seminario.pdf --allow-local-files

clean:
    rm -rf out __pycache__ */__pycache__ .pytest_cache *.pyc *.pyo *.pyd .mypy_cache .coverage dist build *.egg-info