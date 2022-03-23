## Travel time to NHS organisations

[![pages-build-deployment](https://github.com/nhsx/nhs_time_of_travel/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/nhsx/nhs_time_of_travel/actions/workflows/pages/pages-build-deployment) [![Python v3.9](https://img.shields.io/badge/python-v3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

<b>Work in progress</b>

This work was led by [Mattia Ficarelli](https://github.com/mattia-ficarelli), Data Engineer, and [Paul Carroll](https://github.com/pauliecarroll), Senior Data Scientist, as part of their roles with the Analytics Unit of the NHS Transformation Directorate.

### Project Structure

This GitHub repository and accompanying [webpage]( https://nhsx.github.io/nhs_time_of_travel/) contain the initial proof of concept and exploratory analysis for the design of a holistic and interactive mapping tool to support decision-making in health and social care.

A mapping tool could support national and regional commissioning strategies by facilitating the placement of new services and the reconfiguration of existing ones. It could also contribute to the NHS agenda for tackling health inequalities by enabling evidence-based decision-making by providing insight on how the availability of health and social care services is influenced by sociodemographic factors.

Using open-source software and publicly accessible datasets we calculate the travel time, with different modes of transport, to varying NHS healthcare services in London, Cambridge and Lincolnshire. We highlight the challenges of estimating accurate travel times and possible approaches to overcome these. 

### Built With

[![Python v3.8](https://img.shields.io/badge/python-v3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
- [Python v3.9](https://img.shields.io/badge/python-v3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
- [Folium](https://python-visualization.github.io/folium/)
- [OSMnx](https://osmnx.readthedocs.io/en/stable/)
- [NetworkX](https://networkx.org/)

### Getting Started

#### Installation

To get a local copy up and running follow these simple steps.

To clone the repo:

`git clone https://github.com/nhsx/nhs_time_of_travel.git`

### Datasets

The data sources are saved in the nhs_time_of_travel/data, or are widely available with links to the data within the workbooks. 

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

<figure>
  <img src="images/png/cambridge_osmnx_nodes.png" width="400" height="400">
  <figcaption><b>OSMnx walkable urban network of central Cambridge</b></figcaption>
</figure>
