import http.client
import json
import csv

class Graph:

    def __init__(self, with_nodes_file=None, with_edges_file=None):
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0],n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0],e[1]) for e in edges_CSV]



    def add_node(self, id: str, name: str)->None:
        if ',' in name:
            name.replace(',', ' ')
        if (id,name) not in self.nodes:
            self.nodes.append((id,name))
        
    def add_edge(self, source: str, target: str)->None:
        if source!=target and not ((source,target) in self.edges or (target,source) in self.edges):
                self.edges.append((source,target))


    def total_nodes(self)->int:
        return len(self.nodes)


    def total_edges(self)->int:
        return len(self.edges)


    def max_degree_nodes(self)->dict:
        max_deg=0
        max_nodes=set()
        for (id,name) in self.nodes:
            n=0
            for (source,target) in self.edges:
                if id in (source,target):
                    n+=1
            if n==max_deg:
                max_nodes.add(id)
            elif n>max_deg:
                max_deg=n
                max_nodes={id}
        res={}
        for id in max_nodes:
            res[id]=max_deg

        return res


    def print_nodes(self):
        print(self.nodes)


    def print_edges(self):
        print(self.edges)


    def write_edges_file(self, path="edges.csv")->None:
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")



    def write_nodes_file(self, path="nodes.csv")->None:
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")



class  TMDBAPIUtils:

    def __init__(self, api_key:str):
        self.api_key=api_key


    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list=None) -> list: 
        connection = http.client.HTTPSConnection("api.themoviedb.org")
        connection.request("GET","/3/movie/" + movie_id + "/credits?api_key="+self.api_key)
        response = connection.getresponse()
        data = response.read()
        pmcre = json.loads(data)
        if not limit: 
            limit=len(pmcre['cast'])
        res=[]
        for i in range(0,min(limit,len(pmcre['cast']))):
            if str(pmcre['cast'][i]['id']) in exclude_ids:
                continue
            entry={}
            entry['id']=str(pmcre['cast'][i]['id'])
            entry['name']=pmcre['cast'][i]['name']
            entry['credit_id']=pmcre['cast'][i]['credit_id']
            res.append(entry)
        return res


    def get_movie_credits_for_person(self, person_id:str, vote_avg_threshold:float=None)->list:
        connection = http.client.HTTPSConnection("api.themoviedb.org")
        connection.request("GET","/3/person/" + person_id + "/movie_credits?api_key="+self.api_key)
        response = connection.getresponse()
        data = response.read()
        pmcre = json.loads(data)
        if not vote_avg_threshold:
            vote_avg_threshold=0.0
        res=[]
        for i in range(0,len(pmcre['cast'])):
            if pmcre['cast'][i]['vote_average']<vote_avg_threshold:
                continue
            entry={}
            entry['id']=str(pmcre['cast'][i]['id'])
            entry['title']=pmcre['cast'][i]['title']
            entry['vote_avg']=pmcre['cast'][i]['vote_average']
            res.append(entry)
        return res
            

def return_name()->str:
    return "placeholder"


def return_argo_lite_snapshot()->str:
    return 'https://poloclub.github.io/argo-graph-lite/#eb523310-dd07-4034-a676-82856eec5749'


if __name__ == "__main__":

    graph = Graph()
    graph.add_node(id='2975', name='Laurence Fishburne')
    tmdb_api_utils = TMDBAPIUtils(api_key='66c84336add711bccca195ad27e27363')

    graph.write_edges_file()
    graph.write_nodes_file()

    for i in range(3):
        new_graph=Graph(with_nodes_file="nodes.csv",with_edges_file="edges.csv")
        for node in graph.nodes:
            print('finding movie credits for \''+node[1]+'\' ...')
            movies=tmdb_api_utils.get_movie_credits_for_person(node[0],8.0)
            for movie in movies:
                cast=tmdb_api_utils.get_movie_cast(movie_id=movie['id'],limit=3,exclude_ids=[node[0]])
                for person in cast:
                    new_graph.add_node(person['id'],person['name'])
                    new_graph.add_edge(node[0], person['id'])
        graph=new_graph
        graph.write_edges_file()
        graph.write_nodes_file()
