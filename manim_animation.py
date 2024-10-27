from manim import *
from matplotlib import pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from nodes import nodes_def

draw_all = True

DOT_OF_INTEREST = 85

adjacency_matrix = pd.read_csv("ground_truth.csv", header=None).to_numpy()
# create nx graph from adjacency matrix
G = nx.from_numpy_array(adjacency_matrix, create_using=nx.DiGraph)


# create a Manim Dot object for every node in the graph
dot_dict = {}
for node in G.nodes:
    dot_dict[node] = Dot()

edge_dict = {}
for edge in G.edges:
    edge_dict[edge] = Line()

station_dict = {}
for station in nodes_def.keys():
    for node in nodes_def[station]:
        station_dict[node] = station


nx.set_node_attributes(G, dot_dict, "dot")
nx.set_node_attributes(G, station_dict, "station")

nx.set_edge_attributes(G, edge_dict, "edge")


def get_nodes_of_station(station: int):
    return G.subgraph(nodes_def[station])


class GraphFromAdjacencyMatrix(MovingCameraScene):
    def construct(self):
        lightning_bolt = Polygon(
            [
                1,
                2.0,
                0.0,
            ],
            [
                0,
                2.0,
                0.0,
            ],
            [
                -0.75,
                -0.2,
                0.0,
            ],
            [
                0.1,
                0.0,
                0.0,
            ],
            [
                -0.3,
                -2.0,
                0.0,
            ],
            [
                0.75,
                0.3,
                0.0,
            ],
            [
                -0.2,
                0.2,
                0.0,
            ],
            color=RED,
        )

        # show the Dot of interest
        lightning_bolt.set_color(RED)
        lightning_bolt.scale(0.3)
        self.play(Create(lightning_bolt))

        # create text next to the lightning bolt
        doi_text = Text("Problem at sensor 85!")
        doi_text.next_to(lightning_bolt, RIGHT)
        self.play(Write(doi_text))

        self.wait(1)

        doi: Dot = G.nodes[DOT_OF_INTEREST]["dot"]
        doi.set_color(RED)

        self.play(Uncreate(doi_text), run_time=0.5)
        self.play(Transform(lightning_bolt, doi), run_time=1)    
        

        rectangles = []
        rectangle_texts = []
        rect_groups = []
        dot_groups = []
        # for every station
        for i in reversed(range(1, 6)):
            subgraph = get_nodes_of_station(i)
            # create a manim Rectangle object for the station
            height, width = 3, 13
            rect = Rectangle(height=height, width=width, color=BLUE)
            rect.set_stroke(width=2)
            rect.next_to(rectangles[-1] if rectangles else doi, UP)

            rect_text = Text(f"Station {i}")
            rect_text.next_to(rect, RIGHT)
            rectangle_texts.append(rect_text)

            # draw subgraph inside the rectangle
            rect_group = VGroup(rect, rect_text)

            dots_group = VGroup()

            for node in subgraph.nodes:
                if node == DOT_OF_INTEREST:
                    dots_group.add(doi)
                    continue
                dot = subgraph.nodes[node]["dot"]
                margin = 0.4
                dot.move_to(
                    rect.get_center()
                    + np.array(
                        [
                            np.random.uniform(-width / 2 + margin, width / 2 - margin),
                            np.random.uniform(
                                -height / 2 + margin, height / 2 - margin
                            ),
                            0,
                        ]
                    )
                )
                dots_group.add(dot)
            

            # self.play(
            #     Create(rect),
            #     Create(rect_text),
            #     *[Create(dot) for dot in l],
            #     run_time=0.5,
            # )

            # add groups together
            dot_groups.append(dots_group)
            rect_group += dots_group
            rect_groups.append(rect_group)
            self.play(Create(rect_group))

            rectangles.append(rect)
            self.play(self.camera.auto_zoom(rectangles, margin=2), run_time=0.5)

        for i in rect_groups:
            print(i)
        
        # move dot of interest to center of
        doi_target = rectangles[0].get_center()
        doi_target[2] = 0
        self.play(Uncreate(lightning_bolt), run_time=0.01)
        self.play(doi.animate.move_to(doi_target), run_time=0.5)

        external_lines = []
        internal_lines = []
        critical_lines = []

        # Draw edges
        for i in range(1, 6):
            subgraph = get_nodes_of_station(i)
            internal_lines_temp = []
            external_lines_temp = []

            for edge in G.edges:
                start = edge[0]
                end = edge[1]

                start_dot = G.nodes[start]["dot"]
                end_dot = G.nodes[end]["dot"]

                if end == DOT_OF_INTEREST:
                    line = Arrow(
                        start_dot.get_center(),
                        end_dot.get_center(),
                        color=RED,
                        buff=0.1,
                    )
                    critical_lines.append(line)
                elif start in subgraph and end in subgraph:
                    line = DashedLine(
                        start_dot.get_center(),
                        end_dot.get_center(),
                        dashed_ratio=0.7,
                        color=LIGHT_GRAY,
                    )
                    internal_lines_temp.append(line)
                elif start in subgraph or end in subgraph:
                    line = Arrow(
                        start_dot.get_center(),
                        end_dot.get_center(),
                        stroke_width=2,
                        max_tip_length_to_length_ratio=0.05,
                    )
                    external_lines_temp.append(line)
                else:
                    continue

                G.edges[edge]["edge"] = line

            
            self.play(*[Create(line) for line in internal_lines_temp], run_time=0.5)
                
            external_lines.append(external_lines_temp)
            internal_lines.append(internal_lines_temp)

        
        for lines in internal_lines:
            self.play(*[Create(line) for line in lines], run_time=0.5)

        for line in critical_lines:
            self.play(Create(line), run_time=0.5)

        # hide all internal lines
        if draw_all:
            temp = []
            for lines in internal_lines:
                temp += lines
            self.play(*[Uncreate(line) for line in temp], run_time=0.5)

            # hide all arrows
            temp = []
            for lines in external_lines:
                temp += lines
            self.play(*[Uncreate(line) for line in temp], run_time=0.5)

        self.play(
            *[
                G.nodes[node]["dot"].animate.scale(
                    0.15
                    * (len(list(G.predecessors(node))) + len(list(G.successors(node))))
                )
                for node in G.nodes if node != DOT_OF_INTEREST
            ],
            run_time=1,
        )
        
        self.wait(1)

        # get all upstream n
        ancestors = nx.ancestors(G, DOT_OF_INTEREST)

        # color each ancestor red
        ancestors_list = []
        lines_between_ancestors = VGroup()
        for ancestor in ancestors:
            ancestors_list.append(G.nodes[ancestor]["dot"])


            # check if there are any conections between ancestors
            for edge in G.edges:
                start = edge[0]
                end = edge[1]
                if start in ancestors and end in ancestors:
                    if not draw_all:
                        lines_between_ancestors += G.edges[edge]["edge"]
                    ancestors_list.append(G.edges[edge]["edge"])

        # print(ancestors_list)

        self.play(
            *[dot_or_edge.animate.set_color(RED) for dot_or_edge in ancestors_list], run_time=1.0
        )

        # remove all nodes not in ancestors
        nodes_to_delete = []
        print(ancestors)
        for node in G.nodes:
            if node not in ancestors and node != DOT_OF_INTEREST:
                nodes_to_delete.append(G.nodes[node]["dot"])  
        self.play(*[Uncreate(node) for node in nodes_to_delete], run_time=0.5)

        # remove rectangles with no nodes
        rectangles_to_delete = [
            rectangles[1],
            rectangles[2],
            rectangles[4],
        ]
        text_to_delete = [
            rectangle_texts[1],
            rectangle_texts[2],
            rectangle_texts[4],
        ]

            

        self.play(
            *[Uncreate(rect) for rect in rectangles_to_delete],
            *[Uncreate(rect_text) for rect_text in text_to_delete],
            run_time=0.5,
        )

            

        # Set the target positions and sizes for the original rectangles
        rect_groups[0].generate_target()
        rect_groups[0].target.move_to(DOWN * 3)
        

        rect_groups[3].generate_target()
        rect_groups[3].target.move_to(UP * 1)
            
        # Uncreate the lines_between_ancestors
        if lines_between_ancestors:
            self.play(*[Uncreate(line) for line in lines_between_ancestors], run_time=0.5)

        # hide all critical lines
        print(critical_lines)
        self.play(*[Uncreate(line) for line in critical_lines], run_time=0.5)
        

        self.play(
            MoveToTarget(rect_groups[0]),
            MoveToTarget(rect_groups[3]),
            self.camera.frame.animate.move_to(ORIGIN),
            run_time=0.75,
        )

        
        # top row ancestors 
        top_row_ancestors = VGroup()
        bottom_row_ancestors = VGroup()
        for node in G.nodes:
            if node in [16, 6, 37]:
                top_row_ancestors += G.nodes[node]["dot"]
            if node in [13, 28]:
                bottom_row_ancestors += G.nodes[node]["dot"]

        self.play(
            top_row_ancestors.animate.arrange(buff=2.5).move_to(rectangles[3].get_center() + UP * 1),
            bottom_row_ancestors.animate.arrange(buff=2.5).move_to(rectangles[3].get_center() + DOWN * 1),
            run_time=0.5,
        )
                
        # create new read lines between ancestors, lines_between_ancestors
        new_lines_between_ancestors = []
        for edge in G.edges:
            start = edge[0]
            end = edge[1]
            if start in [16, 6, 37, 13, 28] and end in [16, 6, 37, 13, 28]:
                line = Arrow(
                    G.nodes[start]["dot"].get_center(),
                    G.nodes[end]["dot"].get_center(),
                    color=RED,
                    buff=0.1,
                )
                new_lines_between_ancestors.append(line)
                rect_groups[3] += line

        
        # draw new_lines_between_ancestors
        self.play(*[Create(line) for line in new_lines_between_ancestors], run_time=0.5)
        

        # create new critical lines that point to the dot of interest, only with the direct connections
        new_critical_lines = []
        for edge in G.edges:
            start = edge[0]
            end = edge[1]
            if end == DOT_OF_INTEREST:
                line = Arrow(
                    G.nodes[start]["dot"].get_center(),
                    G.nodes[end]["dot"].get_center(),
                    color=RED,
                    buff=0.1,
                )
                new_critical_lines.append(line)
        
        # draw new_critical_lines
        self.play(*[Create(line) for line in new_critical_lines], run_time=0.5)
        
        self.play(self.camera.frame.animate.move_to(ORIGIN), run_time=0.5)
        self.play(self.camera.frame.animate.scale(0.75), run_time=0.3)
        
        # add labels to nodes to ancestors and dot of interest
        for node in G.nodes:
            if node in [16, 6, 37, 13, 28, DOT_OF_INTEREST]:
                dot = G.nodes[node]["dot"]
                label = Text(f"{node}")
                label.next_to(dot, UP)
                rect_groups[3] += label
        
        # draw labels 
        self.play(*[Create(label) for label in rect_groups[3] if isinstance(label, Text)], run_time=0.5)
        
        



        #### BEGIN END TITLE ####

        # Create the end title
        end_title = Text("The End").scale(2)
        end_title.set_color(RED)
        credits = Text("Operators of the Neuron for Bosch").scale(1)
        credits.set_color(RED)
        credits.next_to(end_title, DOWN)

        end_title_copy = G.nodes[DOT_OF_INTEREST]["dot"].copy()
        self.add(end_title_copy)
        
        # remove doi from the rect_groups[0]
        rect_groups[0].remove(G.nodes[DOT_OF_INTEREST]["dot"])
        
    
        # Transform all elements into the end title
        self.play(
            FadeOut(rect_groups[0]),
            FadeOut(rect_groups[3]),
            *[FadeOut(line) for line in new_critical_lines],
            run_time=2
        )

        self.play(Transform(end_title_copy, end_title), run_time=1)

        self.wait(1)

        self.play(Write(credits), run_time=1)

        self.wait(1)

    
