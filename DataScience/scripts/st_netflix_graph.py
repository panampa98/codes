import streamlit as st
import json
import pandas as pd

graph_data = {}

df = pd.read_csv('DataScience/datasets/netflix-shows/netflix_titles.csv')

df_edges = df[['title', 'director']].drop_duplicates().dropna().reset_index(drop=True).copy()
df_edges.columns = ['source', 'target']

graph_data['links'] = df_edges.to_dict(orient='records')

degree_counts = df['director'].value_counts().to_dict()
director_list = [{'id': director, 'degree': count, 'group': 0} for director, count in degree_counts.items()]

degree_counts = df['title'].value_counts().to_dict()
titles_list = [{'id': director, 'degree': count, 'group': 1} for director, count in degree_counts.items()]

graph_data['nodes'] = director_list + titles_list

graph_json = json.dumps(graph_data)

html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        svg {{ width: 100%; height: 900px; border: 1px solid black; }}
        .node {{ transition: fill 0.3s; }}
        .link {{ stroke: gray; stroke-width: 2px; transition: stroke-width 0.3s; }}
        text {{ font-size: 12px; fill: black; pointer-events: none; }}
    </style>
</head>
<body>
    <svg></svg>
    <script>
        const width = window.innerWidth * 0.8;
        const height = 500;
        const graph = {graph_json};

        const color = d3.scaleOrdinal(d3.schemeCategory10);  

        const svg = d3.select("svg")
            .attr("width", width)
            .attr("height", height);

        const container = svg.append("g"); // Grupo que se moverá con el zoom

        // Agregar zoom al SVG
        svg.call(d3.zoom()
            .scaleExtent([0.1, 3]) // Zoom mínimo y máximo
            .translateExtent([[-width, -height], [2 * width, 2 * height]]) // Evita que el grafo desaparezca
            .on("zoom", (event) => {{
                container.attr("transform", event.transform);
            }}));

        const simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.links).id(d => d.id).distance(10))
            .force("charge", d3.forceManyBody().strength(-10))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = container.selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link");

        const node = container.selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 10)
            .attr("fill", d => color(d.group !== undefined ? d.group : 0))
            .on("mouseover", highlight)
            .on("mouseout", reset)
            .call(drag(simulation));

        const text = container.selectAll("text")
            .data(graph.nodes)
            .enter().append("text")
            .attr("dx", 12)
            .attr("dy", 4)
            .text(d => d.id);

        function highlight(event, d) {{
            node.attr("fill", n => n.id === d.id || graph.links.some(l => (l.source.id === d.id && l.target.id === n.id) || (l.target.id === d.id && l.source.id === n.id)) ? "orange" : color(n.group));
            link.attr("stroke", l => l.source.id === d.id || l.target.id === d.id ? "red" : "gray")
                .attr("stroke-width", l => l.source.id === d.id || l.target.id === d.id ? 4 : 2);
        }}

        function reset() {{
            node.attr("fill", d => color(d.group));
            link.attr("stroke", "gray").attr("stroke-width", 2);
        }}

        function drag(simulation) {{
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}

            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            text
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=850)


# Simulación de datos de recomendaciones con grupo de nodos
# graph_data = {
#     "nodes": [
#         {"id": "Netflix", "group": 1},
#         {"id": "Breaking Bad", "group": 2},
#         {"id": "Stranger Things", "group": 2},
#         {"id": "HBO", "group": 1},
#         {"id": "Game of Thrones", "group": 2},
#         {"id": "Chernobyl", "group": 2},
#         {"id": "Better Call Saul", "group": 2}
#     ],
#     "links": [
#         {"source": "Netflix", "target": "Breaking Bad"},
#         {"source": "Netflix", "target": "Stranger Things"},
#         {"source": "HBO", "target": "Game of Thrones"},
#         {"source": "HBO", "target": "Chernobyl"},
#         {"source": "Breaking Bad", "target": "Better Call Saul"},
#         {"source": "Breaking Bad", "target": "Stranger Things"}
#     ]
# }