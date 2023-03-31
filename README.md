## MedicalMap

[![status: experimental](https://github.com/GIScience/badges/raw/master/status/experimental.svg)](https://github.com/GIScience/badges#experimental)

This is a prototype, and a concept piece of work for the NHS.

This work was led by [Paul Carroll](https://github.com/pauliecarroll), Senior Data Scientist, with a team comprising of [Oliver Jones](https://github.com/oliverjonesnhsx), [Muhammed-Faaiz Shawanas], [Mary Amanuel], from NHS England, [Max Morisov] & [Nick Fortescue], engineers at GoogleHealth.

The following page and accompanying [GitHub repository](https://github.com/nhsx/nhs_time_of_travel) contain the initial proof of concept and exploratory analysis for the design of a holistic and interactive mapping tool to support decision-making in health and social care.

A mapping tool could support national and regional commissioning strategies by facilitating the placement of new services and the reconfiguration of existing ones. It could also contribute to the NHS agenda for tackling health inequalities by enabling evidence-based decision-making by providing insight on how the availability of health and social care services is influenced by sociodemographic factors.

Using open-source software and publicly accessible datasets we're able to show three pages here so far; The first, Multiple Shortest Routes, this can be used for staff routes to work. The second, Max Coverage Location, this can be used to score a site, e.g. a covid site or a new GP practice. Third, the Travelling Salesman Problem; in a health context this could be used to plan district nurse visits, or for ambulance drop-offs.

Data sources: [NHS Digital](https://digital.nhs.uk/services/organisation-data-service/file-downloads/gp-and-gp-practice-related-data), [Uber Movement](https://movement.uber.com/)

<hr class="nhsuk-u-margin-top-0 nhsuk-u-margin-bottom-6">

### Project Aims

The project was set up following feedback from several areas of the NHS, who responded to the original time_to_travel work that was presented at the NHS Pycom conference in 2022, [here](https://github.com/nhsx/nhs_time_of_travel/) and [here]( https://nhsx.github.io/nhs_time_of_travel/).
Following this a collaboration took place with Googlehealth and Pycom combining to work on a week by week project looking to solve some of the Geospatial problems that the NHS faces on a daily basis. 
As the work developed, different areas of the NHS who use geospatial tools became more aware of the work, and a decision was made to build a piece of software that could be taken to NHS trusts and to the data herewithin. The aim being to keep the tool flexible, open, open-source, and adaptable. By keeping all the coding in python, we hope this opens up this tool to be adapted to different use cases by many different users, across the varying parts of the NHS. 

### Built With

[![Python v3.10](https://img.shields.io/badge/python-v3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
- [Folium](https://python-visualization.github.io/folium/)
- [OSMnx](https://osmnx.readthedocs.io/en/stable/)
- [NetworkX](https://networkx.org/)

### Getting Started

### Installation

To clone the repo:

`git clone https://github.com/nhsx/nhs_time_of_travel.git`


cd into the streamlit folder. Once there please follow these instructions:

Unix/macOS
```bash
pipenv install --python 3.10
pipenv install -r requirements.txt
pipenv shell
```

This was launch your pip environment with the necessary installations and dependencies. 
Once this is open run "conda install cartopy". 

Finally to launch the streamlit app:
```bash
streamlit run streamlit_app.py
```

### Datasets

The data sources are saved for your use in the data folder in the repo, or are widely available with links to the data within the workbooks. 

### Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

_See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidance._

### License

Distributed under the MIT License. _See [LICENSE](./LICENSE) for more information._


