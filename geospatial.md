# Interactive Geospatial Decision Making Tool: Requirements Specification
 
## Background:
There is a desire to create a holistic and interactive mapping tool which includes agreed parameters with the aim to support decision-making in health and social care.
 
### Problem Statement:

1. No example tool which can be reused for different geospatial decision making projects. 

2. Many useful components are available but not connected together in a NHS-specific user friendly way.

What are the current alternatives?:
See a open-source compiled list [Here](https://github.com/CUTR-at-USF/awesome-transit). (In particular: Openrouteservices; OpenTripPlanner; Shape Place; Targomo; TravelTime; Nominatim).

Proof of concept prototype [Here](https://nhsx.github.io/nhs_time_of_travel/) which demonstrates the use of the python libraries to calculate and visualise a small area, creating isochrones for difference modes of transport including data on times of day and additional transport networks.  A search function has also been demonstrated which would add a more flexible feature to the tool.
 
### Aim and Objectives:
The solution should look to:

1. Support evidence for the placement/removal of services

2. Enable linking health and social care datasets to explore wider determinants of health

3. Support stakeholder influencing via good data presentation
 
### Brief Overview of Proposed Solution:

A containerised tool or open library which provides user-interactive features (possible through web app).  The tool would connect to free and open APIs and live NHS data sources to enable up-to-date data flows.  The tool would use the Python libraries OSMnx, networkX, geopandas and folium implementation of travel times calculations and visualisations.  Additional data sheets could be imported as CSVs in order to plot demographics or socio-economic variables alongside services and catchment isochrones.  

### Non-Functional Requirements (NFR):

| NFR | Specification |
| ------- | ---------|
| Security | None - Open Source Distribution |
| Responsiveness | Load mapping views within 3 seconds. Update interface and interaction within 2 seconds. Run calculations within 60 seconds |
| Scalability | 1 user | 
| Internationalisation | Python |
| Cross-platform | Windows and MacOS (web application) |
| Compliance | Not Stated |
| Accessibility | Not Stated |
 
### Features and Scenarios:

**1. Feature:** Tool to cover the England and Wales geography. 

**2. Feature:** View by different healthcare spatial hierarchy, and zoom into health (region, ICS, CCG, Clinical Networks)  and demographic geographies (MSOA, LSOA). Full list [Here](https://www.ons.gov.uk/methodology/geography/ukgeographies/healthgeography) and [Here](https://webarchive.nationalarchives.gov.uk/ukgwa/20220401215420/https:/www.ons.gov.uk/methodology/geography/ukgeographies/censusgeography). The ability to select different geography is selected from a drop down list. Best for the default view to be a zoomed in view of the geography (e.g. Shrewsbury rather than full England and Wales to speed tool loading up). Needs to cover standard NHS use-cases, mapping a table of location based data to a chloropleth overlay for all health geographies & deal with point (GP) vs area (PCN) visualisations. PCNs currently don’t have a map, so there would need to be thought about how to create these, e.g. hex based from GP Practice. 

**3. Feature:** Map acute hospitals, GP practices, other health settings (NB: Need exhaustive list defining). This would allow a user to visualise common healthcare services as point markers based on their location, see the distribution of selected services for a selected geography. A service tick box is used to to visualise the different service layers individually. 

**4. Feature:** Indication of terrain (rural; motorways; A roads; B roads)

**5. Feature:** Tool to be able to map catchment areas (isochrones) for different health services. For example the area 20 min drive away from a hospital. 

**6. Feature:** Tool to map point to point travel times for different transportation modes at different times of day/night. Ideally, would incorporate live travel time data.

**7. Feature:** Tool to be able to incorporate imported data relating to deprivation indexes, ethnicities and socio-demographic profiles,  life-expectancy, premature mortality, employment, education, income, wealth, access to green spaces, patient feedback and self-reporting measures such as Patient Reported Outcome Measures (PROMs), National Cancer Patient Experience Survey (CPES).

**8. Feature:** Visualisation of flows along routes (e.g. number of patients) 

**9. Feature:** Tool to allow adding data for past, present, expected activity levels - number of patients/cases and simulate patient flows.

**10. Feature:** Tool to allow to add provider capacity data (e.g 1 hospital has capacity to treat up to 100 patients in a month; if we expected 3000 cases pa, how many centres can handle this workload?)
