<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 

## Travel time to NHS organisations

The following page and accompanying GitHub repository contain the initial proof of concept and exploratory analysis for the design of a holistic and interactive mapping tool to support decision-making in health and social care.

A mapping tool could support national and regional commissioning strategies by facilitating the placement of new services and the reconfiguration of existing ones. It could also contribute to the NHS agenda for tackling health inequalities by enabling evidence-based decision-making by providing insight on how the availability of health and social care services is influenced by sociodemographic factors.

Using open-source software and publicly accessible datasets we calculate the travel time, with different modes of transport, to varying NHS healthcare services in London and Cambridge. We highlight the challenges of estimating accurate travel times and possible approaches to overcome these. 

Data sources: [NHS Digital](https://digital.nhs.uk/services/organisation-data-service/file-downloads/gp-and-gp-practice-related-data), [Uber Movement](https://movement.uber.com/)

<hr class="nhsuk-u-margin-top-0 nhsuk-u-margin-bottom-6">

<div class="nhsuk-warning-callout">
  <h3 class="nhsuk-warning-callout__label">
    Data Quality<span class="nhsuk-u-visually-hidden">:</span>
  </h3>
  <p>Data Quality placeholder. 
  </p>
</div>

### Walking time to GP practices in Cambridge 

Cambridge was selected as a case city to explore the walking distance to GP practices due to its relatively small size and because central Cambridge is well defined by the CB1, CB2, CB3, CB4, and CB5 postcodes (highlighted in blue in the Cambridge postcode map). The currently active GP practices within the central Cambridge postcode areas were extracted from the [EPRACCUR dataset](https://digital.nhs.uk/services/organisation-data-service/file-downloads/gp-and-gp-practice-related-data), which contains data for general Medical Practices supplied by the NHS Prescription Services and published by NHS Digital.

Using the [GeoPy library](https://geopy.readthedocs.io/en/stable/#) and the [Nominatim API](https://nominatim.org/) the coordinates for the central Cambridge GP practices were identified from GP Practice postcodes. GeoPy allows for the use of multiple different geolocation services, including Google Maps and Bing Maps. Nominatim was selected as it is free to use (limited to a maximum of 1 request per second) and because it is integrated with OpenStreetMap. Due to its usage limits, Nominatim is not suitable for heavy use and does not support systematic queries. Before using Nominatim please read its [usage policy](https://operations.osmfoundation.org/policies/nominatim/).

The [Folium library](https://python-visualization.github.io/folium/) was used to map the GP practices in central Cambridge using their coordinates. Click on an individual marker for the GP practice name, code, address, and contact information.

<p align="left">
  <iframe width= "455" height="455"  src="images/folium/cambridge_postcode_map.html" style="border:none;"></iframe>
  &nbsp; &nbsp;
  <iframe width= "455" height="455"  src="images/folium/cambridge_map_no_travel.html" style="border:none;"></iframe>
</p>

<div class="nhsuk-action-link">
  <a class="nhsuk-action-link__link" href="data/cambridge_gp_practices.csv">
    <svg class="nhsuk-icon nhsuk-icon__arrow-right-circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M0 0h24v24H0z" fill="none"></path>
      <path d="M12 2a10 10 0 0 0-9.95 9h11.64L9.74 7.05a1 1 0 0 1 1.41-1.41l5.66 5.65a1 1 0 0 1 0 1.42l-5.66 5.65a1 1 0 0 1-1.41 0 1 1 0 0 1 0-1.41L13.69 13H2.05A10 10 0 1 0 12 2z"></path>
    </svg>
    <span class="nhsuk-action-link__text">Download the Cambridge GP practice dataset (.csv)</span>
  </a>
</div>

Text here. 

<p align="left">
  <img src="images/png/cambridge_osmnx_nodes.png" width="460" height="460">
  &nbsp; &nbsp;
  <img src="images/png/cambridge_node_coloured.png" width="460" height="460">
</p>

<p align="left">
  <img src="images/png/cambridge_isochromes_coloured.png" width="460" height="460">
  &nbsp; &nbsp;
  <iframe width= "455" height="455"  src="images/folium/cambridge_map_travel.html" style="border:none;"></iframe>
</p>


### Driving time between a GP Practice and a Hospital in central London

<p>
Placeholder text. 
</p>

<p align="left">
  <img src="images/png/london_osmnx_nodes.png" width="460" height="460">
  &nbsp; &nbsp;
  <iframe width= "455" height="455"  src="images/folium/route_map.html" style="border:none;"></iframe>
</p>

<p align="left">
  <iframe width= "960" src="images/folium/plotly_table.html" style="border:none;"></iframe>
</p>

<div class="nhsuk-action-link">
  <a class="nhsuk-action-link__link" href="data/uber_movement_speeds_6pm.csv">
    <svg class="nhsuk-icon nhsuk-icon__arrow-right-circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M0 0h24v24H0z" fill="none"></path>
      <path d="M12 2a10 10 0 0 0-9.95 9h11.64L9.74 7.05a1 1 0 0 1 1.41-1.41l5.66 5.65a1 1 0 0 1 0 1.42l-5.66 5.65a1 1 0 0 1-1.41 0 1 1 0 0 1 0-1.41L13.69 13H2.05A10 10 0 1 0 12 2z"></path>
    </svg>
    <span class="nhsuk-action-link__text">Download the Uber Movement dataset (.csv)</span>
  </a>
</div>

## About this page

This page is built using end-to-end open source analytical tools including: [The NHS Digital Service Manual](https://service-manual.nhs.uk/), [python](https://nhs-pycom.net/), [plotly](https://plotly.com/python/), [folium](http://python-visualization.github.io/folium/), [geopy](https://geopy.readthedocs.io/en/stable/), [beautiful soup](https://www.crummy.com/software/BeautifulSoup/), [github.io](https://pages.github.com/), and [github actions](https://github.com/features/actions).

<div class="nhsuk-action-link">
  <a class="nhsuk-action-link__link" href="https://github.com/nhsx/open-analytics-template">
    <svg class="nhsuk-icon nhsuk-icon__arrow-right-circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M0 0h24v24H0z" fill="none"></path>
      <path d="M12 2a10 10 0 0 0-9.95 9h11.64L9.74 7.05a1 1 0 0 1 1.41-1.41l5.66 5.65a1 1 0 0 1 0 1.42l-5.66 5.65a1 1 0 0 1-1.41 0 1 1 0 0 1 0-1.41L13.69 13H2.05A10 10 0 1 0 12 2z"></path>
    </svg>
    <span class="nhsuk-action-link__text">Find out how to build your own open analytics pipeline</span>
  </a>
</div>

If you have any suggestions or questions, email: <a href="mailto:mattia.ficarelli@nhsx.nhs.uk">mattia.ficarelli@nhsx.nhs.uk</a> or <a href="mailto:paul.carroll@nhsx.nhs.uk">paul.carroll@nhsx.nhs.uk</a>

<hr class="nhsuk-u-margin-top-0 nhsuk-u-margin-bottom-6">
