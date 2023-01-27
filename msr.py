import os
!pip3 install -r requirements.txt


# format the hospital dataset example
def hospital_data():
    hospitals = pd.read_csv('data/Hospital.csv',sep=',')
    hospitals = hospitals.dropna(subset=['County'])
    hospital = hospitals[(hospitals['City'].str.contains ('Cambridge'))].reset_index(drop = True)
    hospital['Address'] = hospital[['Address2', 'Address3', 'City','County',]].astype(str).agg(', '.join, axis=1)
    hospital['Address'] = hospital['Address'].str.title() 
    hospital['Address'] = hospital['Address'].str.replace('Nan', '').str.replace(' ,', ' ')
    hospital['Name'] = hospital['OrganisationName'].str.title()
    hospital = hospital[['Name', 'Address']]
    
    return hospital


def main():
    df=hospital_data()
    #df.drop(index=2,inplace=True)
    ox.config(log_console=True, use_cache=True)

    target_address = "35 Clarendon Street, Cambridge"
    target_location = ox.geocode(target_address)
    target = ox.nearest_nodes(G, target_location[1],Y=target_location[0])


    
    coords = []
    for address in df.Address:
        try:
            coords.append(ox.geocoder.geocode(address))
        except Exception as e:
            pass

    list=[]
    for i,c in enumerate(coords):
        list.append(ox.nearest_nodes(G,X=coords[i][1],Y=coords[i][0]))

    routes = []
    for i,a in enumerate(list):
        routes.append(nx.shortest_path(G,list[i],target,weight="length")) 

    lengths=[]
    for i,b in enumerate(routes):
        lengths.append(nx.shortest_path_length(G,source=list[i],target=target,weight='length'))

    Gx= ox.plot_graph_routes(G, routes,route_linewidth=6,bgcolor='k');

    df['lengths'] = np.array(lengths)
    df['lengths']= round(df.lengths,0)

    return Gx, df



if __name__=='__main__':
    main()

