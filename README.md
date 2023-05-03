## MedicalMap

[![status: experimental](https://github.com/GIScience/badges/raw/master/status/experimental.svg)](https://github.com/GIScience/badges#experimental)

This is a prototype, and a concept piece of work for the NHS.

This work was led by [Paul Carroll](https://github.com/pauliecarroll), Senior Data Scientist, with a team comprising of [Oliver Jones](https://github.com/oliverjonesnhsx), [Muhammed-Faaiz Shawanas](https://github.com/faaiz-25), [Mary Amanuel](https://github.com/maryamanuel1), from NHS England, [Max Morisov](https://github.com/maxim-morosov) & [Nick Fortescue](https://github.com/nickfortescuegoogle), engineers at GoogleHealth.

The following page and accompanying [GitHub repository](https://github.com/nhsx/nhs_time_of_travel) contain the initial proof of concept and exploratory analysis for the design of a holistic and interactive mapping tool to support decision-making in health and social care.

A mapping tool could support national and regional commissioning strategies by facilitating the placement of new services and the reconfiguration of existing ones. It could also contribute to the NHS agenda for tackling health inequalities by enabling evidence-based decision-making by providing insight on how the availability of health and social care services is influenced by sociodemographic factors.

Using open-source software and publicly accessible datasets we're able to show three pages here so far; The first, Route Optimisation, a.k.a. the Travelling Salesman Problem; in a health context this could be used to plan district nurse visits, for ambulance drop-offs, or for blood packages deliveries. It has a multitude of uses. The second, Multiple Shortest Routes, this can be used for staff routes to work, and to reduce emissions, a focus that is gaining importance for NHS travel planners. Third, Max Coverage Location, this can be used to score a site, e.g. a covid site or a new GP practice.

Data sources: [NHS Digital](https://digital.nhs.uk/services/organisation-data-service/file-downloads/gp-and-gp-practice-related-data), [Uber Movement](https://movement.uber.com/)

<hr class="nhsuk-u-margin-top-0 nhsuk-u-margin-bottom-6">

### Project Aims

The project was set up following feedback from several areas of the NHS, who responded to the original time_to_travel work that was presented at the NHS Pycom conference in 2022, [here](https://github.com/nhsx/nhs_time_of_travel/) and [here]( https://nhsx.github.io/nhs_time_of_travel/).
Following this a collaboration took place with Googlehealth and Pycom combining to work one day a week on a project looking to solve some of the Geospatial problems that the NHS faces on a daily basis. 
As the work developed, different areas of the NHS who use geospatial tools became more aware of the work, and a decision was made to try to build a piece of software that could be taken to NHS trusts and to the data herewithin. The aim being to keep the tool flexible, open, open-source, and adaptable. By keeping all the coding in python, we hope this opens up this tool to be adapted to different use cases by many different users, across the varying parts of the NHS. 

### Built With

[![Python v3.10](https://img.shields.io/badge/python-v3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
- [Folium](https://python-visualization.github.io/folium/)
- [OSMnx](https://osmnx.readthedocs.io/en/stable/)
- [NetworkX](https://networkx.org/)

## Getting Started

## Installation

To clone the repo:

`git clone https://github.com/nhs-pycom/nhs_time_of_travel.git`


cd streamlit, into the streamlit folder. Once there please follow these instructions:

Unix/macOS
```bash
pip install pipenv (if you don't have pipenv installed)
pipenv install --python 3.10
pipenv install -r requirements.txt
pipenv shell
```

This was launch your pip environment with the necessary installations and dependencies. 

Finally to launch the streamlit app:
```bash
streamlit run streamlit_app.py
```

## Instructions to use the Streamlit app once this has been spun up

When the Streamlit app is working, you should see the NHS logo, a train, and 'MedMap - NHS Geospatial Tool', followed by a description of the tool.
On the left is an index, with the 'streamlit app' highlighted. This index allows you to access the pages within the tool. 
For example if you select 'Route Optimzer', this page will load, and likewise the following two other pages. I'll walk you through how to use each of these now. 

## Route Optimizer page (aka the Travelling Salesman Problem)

- Select the Route Optimizer page from the left index. 
- Here to use the page you will need data. The NHS Digital Hospital Dataset for England and Wales comes loaded as a default. Within the data folder in the repo, you'll also have access to the epraccur dataset, this is NHS England's GP Practice dataset. 
- If you wish to use your own data, there is a templates folder, and within that Address_template.xlsx. Please enter the addresses you wish to use, in the format specified in this worksheet. If you change the format, the code will likely break, so please follow the format of this workbook. 
- To access other files apart from Hospital.csv, on the left of the page below the page selector, if a 'browse files' button. If you click here, this will access your computer, where you can load the Address_template, or the epraccur dataset, or any other dataset you've prepared in the same format as the Address_template.
- Next, in the box titled 'Enter Town/ City or County (or both), either select a location from the dropdown, or delete what's in the box and type the town/city/ county you want the data for, for this page. This box filters the Hospital dataset to just the town/ city/ county you wish to inspect. The filtered dataframe will be visible once you've done this.
- If you have start address that isn't the uploaded data, please enter it now in the 'Enter a new start address' field, please follow the format like this, '65 Goldsworth Road, Woking'.
- If you've entered a start address, select the network type from the dropdown, and hit the 'Submit' button. Your start address will now appear as the start address in two fields.
- If you haven't entered a start address, select one from the dropdown. 
- Once you hit 'Submit', the algorithm will run, and will load the map, the route, ordered markers for each location, and a dataframe underneath the map. This dataframe shows each stage of the route, from and to, the distance for that stage, and the total distance. 
- You can select a different start address, hit submit, and redo the order and map.
- Please note two caveats. More than 10 addresses, and the program will be slow. At 10, the numbers of permutations is approximately 3.6 million. At 12, this is 479 million. Additionally the first time you run this map for a large or densely roaded area, such as London, Cornwall, North Yorkshire, Manchester, the map may take a few minutes to run. This is the due the complexity of nodes and edges needed in the required area. The program stores this map as a json file the first time you run it, and the second time and ongoing, the load time will be a lot faster as this json file is used. Please note this does not apply to your data, only the background map, which is called from an api request. Your data will never leave the computer you're using to run this app. 
- Lastly the solution presented here uses two algorithms, a permutations travelling salesman (tsp) algorithm, and a greedy tsp algorithm, both results are plotted onto a networkx nodes and edges map, and the shorter total distance is taken as the metric for the best route. This is by no means an exhaustive practice, and I'm sure there are better solutions out there, but in the interests of running this on standard computer, laptop, or interface to a TRE, this was the current best solution we could find. If you can suggest something better, please drop us a line and let us know. 


### Multiple Shortest Route page

- The start functionality is the same as the previous as regards data uploading. The Hospital dataset comes as pre-loaded, so I'll run through the rest of the instructions using this dataset.
- Select town/ city/ county (or both) from the 'Enter Town/ City or County (or both)' selector. This will filter the dataframe to that location.
- Enter your target address in the titled box, in the following format, '2 Hill Road, Cambridge'.
- Select the network type. 
- Hit Submit.
- Your map with shortest routes and a dataframe should be displayed.


### Max Coverage Location page

- Here the first box is where you enter your location to score.
- The next box is radius around this location, here select from 1 to 5 miles. Please use the + and - symbols to increase or decrease the radius. This is limited to 5 currently in the code. 
- To find out time to travel, select the travel speed from the dropdown. This can be walking at 3mph, driving peak urban 10mph, driving off peak urban 20mph, or driving rural 34mph. Average driving times are taken from gov.uk, https://www.gov.uk/government/statistical-data-sets/average-speed-delay-and-reliability-of-travel-times-cgn.


### Datasets

Accessible in the 'data' folder, all of these are publicly available, either from NHS Digital or ONS. The two that we default to use in the examples are the NHS Digital 'Hospital' dataset, a csv of public and private NHS England & Wales hospitals. The second is the eppracur dataset, the NHS Digital of GP practices in England and Wales.


### Templates

This is a folder with a template for entering your own addresses. I've left a sample of five care homes here in York. The only necessity here is to enter the format in the columns provided, 'Name', 'Address', 'City', 'County', & 'Postcode'. You will need to follow this format and enter the details as per the examples in the template.
The code is set up to read the format, and will geocode the addresses if you follow this format. 


### Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.
Please also reach out if you any have page suggestions, or comments. We've very interested to know if you fork the repo, and take the work further. There's also an issues tab, if there are any issues with the existing code, please raise an issue here.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

_See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidance._

### License

Distributed under the MIT License. _See [LICENSE](./LICENSE) for more information._


