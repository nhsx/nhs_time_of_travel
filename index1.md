

### MedMap - A NHS Geospatial Tool

This was led by [Paul Carroll](https://github.com/pauliecarroll), Senior Data Scientist, at the Digital Analytics & Research Team at NHS England, with a team comprising of 
[Oliver Jones](https://github.com/oliverjonesnhsx), [Muhammed-Faaiz Shawanas](https://github.com/faaiz-25), [Mary Amanuel](https://github.com/maryamanuel1), from NHS England, & 
[Nick Fortescue](https://github.com/nickfortescuegoogle), [Max Morisov](https://github.com/maxim-morosov) engineers at GoogleHealth, without who this work would not be where it is. 
 
The following [GitHub repository](https://github.com/nhsx/nhs_time_of_travel) contains the initial proof of concept and exploratory analysis for the design of a holistic and interactive 
mapping tool to support decision-making in health and social care. This work was carried out by carried out by [Mattia Ficarelli](https://github.com/mattia-ficarelli), Data Engineer, 
and [Paul Carroll](https://github.com/pauliecarroll).

The work that follows can be seen and downloaded from this repository [GitHub repository](https://github.com/nhs-pycom/nhs_time_of_travel). This is the current piece of work to which the 
following page refers to. Please raise any issues with the code using the issues part of the github repository. 


### Use-cases 

Following a presentation at NHS-Pycom on the aforementioned Geospatial work, several different areas of the NHS got in touch, and they identified where there are current gaps and needs, 
or use-cases for which a geospatial tool, built specifically for purpose, could help solve the issues they faced. The use-cases they faced were numerous:

- Ambulance drop-offs/ Patient transport
- District Nurse visits
- blood deliveries
- Managing a multi-site portfolio and the transport units within
- Modes and means of transport for NHS staff to their place or places of work, and the environmental impact of their travel
- Carbon reduction and the evidence base for sustainability in order to support external conversations 
- Where to site a new Covid site for maximum population and minimum overlap with other sites
- Where to site a Diabetes or blood test van in order to cut missed appointments for patients by making it easier for them to access services.


### Our Angle -  Cost & Data. Solve these two problems.

The more we spoke to different areas of the NHS the more this need became apparent. What also became apparent was the cost of some of these services. Numerous trusts are paying commercial 
operators for these services. Sometimes these were the only operators out there, as there was nothing publicly available or free. 
But for other services the second need was the need for patient and staff data to remain confidential, and remain within the trust. Within the NHS data protection is paramount, so taking 
this account, we wanted to build a tool that could be brought to the data. Using open-source software and publicly accessible datasets we calculate the travel time, we wanted to show 
what is possible and bring to the different areas of the NHS for them to adapt to their specific needs. Two publicly available datasets we have used are from NHS Digital. The main software
we used is Python 3.8+, and Streamlit, with a succession of Geospatial libraries within Python.
This app can be spun up on anyone's laptop, and the data would never need to leave that machine. 

Data sources: [NHS Digital](https://digital.nhs.uk/services/organisation-data-service/file-downloads/gp-and-gp-practice-related-data).


### What our tool does -  Streamlit

Streamlit is an app wrapper, extremely useful and malleable. Especially so when it comes to geospatial work. I carried out some research on Geospatial tools and the best way to approach 
multiple functionalities, and the shining example of this is this page https://github.com/opengeos/streamlit-geospatial. Professor [Qiusheng Wu] https://github.com/giswqs and his 
geospatial page showed us what was possible, and gave us a great example of how to go after certain geospatial tasks, and write the code for how to have these differing geospatial 
functions run together in one app and one place. 


### Three Pages .... so far

### Route Optimisation - aka The Travelling Salesman Problem

To tackle the use-cases of Ambualnce drop-offs/ Patient transport, District Nurse visits, or blood deliveries, it became clear the issue here to solve, was one of route optimisation. 
I researched how to go about this online, read several medium articles and also read through several github repositories. In computer science this problem is a NP hard problem, and there 
were no easy solutions out there. There were also quite a few commercial operators in this space, and rightly so, for 10 different addresses, 10 permutations with P(10, 10) gives 3.6 
million approximate outcomes, with 12 addresses this goes up significantly to 479 million. Trying to solve this problem in way that would be computationally relevant for the likely 
laptop power in a NHS trust was a real need here. But also there was a sweetspot. How many patients was a district nurse likely to visit in a day. How many patient drop-offs would there 
be before an ambulance would need to return to hospital, especially in this post covid world. Both of these answers we'd imagine would be less than 12. 
I took the approach of trying to solve the permutations question first, and plotting that route on to a folium map, and measuring it. Using the OSMNX package, in combination with 
[NetworkX](https://networkx.org/documentation/stable/index.html)
and Folium, we were able to achieve this. 

OSMnx is a Python package that lets you download geospatial data from [OpenStreetMap](https://www.openstreetmap.org/) and model, project, visualise and analyse real-world street networks 
and any other geospatial geometries, including walkable, drivable, or bikeable urban networks. A network is a collection of connected objects. The objects in a network are called 
nodes (or vertices) and are visualised as points. The connections between nodes are called edges and are drawn as lines.  OSMnx networks are topologically corrected, directed, 
and preserve one-way directionality. 

Layering the OSMNX and NetworkX nodes and edges onto a Folium map, and using the ox.distance.nearest_nodes and nx.shortest_path functions, we were able to produce a calculation of the 
shortest route around the network. The algorithm we've written does this first for a permutations function, and then for a tsp_greedy function. This is a function where the first address 
to second address is the shortest distance, and then the third address is selected from the next shortest distances available from the remaining addresses not yet visited. 
From testing, having the initial permutations distance calculation compare with the tsp_greedy calculation, returned a far more superior output to the route displayed on the folium map. 
This also gave an update you could see visibly you would drive, or walk. 

The functions are wrapped in the streamlit code, and when the code to run the app is called 'streamlit run streamlit_app.py', this is the page that you'll see when you click on the Route
Optimizer 

