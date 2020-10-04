# PyPani
"PyPani" is a python package, provides irrigation scheduling based weather, soil, vegetation stage, and crop types. It can be incorporated with a real-time forcasting model with sufficient environmental information and can simplistically recommend irrigation requirements to the farmers and small agriculture stakeholders.  The module concept was originally proposed by an international group of research institutes [1] in a project named "[The STARS Project](https://www.stars-project.org/en/about-us/the-stars-project/)". Later, the International Wheat and Maize Organization Bangladesh, extend the idea, and thus the model is developed as for python users.

The core functionality of the model can be elaborated in the following diagram. There are four sub-modules that connect the core model: 
Weather module: It takes the observed and forecasted weather data for the model. The module supports daily weather data with a seven-day weather forecast. For the most basic evapotranspiration calculation approach,  it requires daily maximum and minimum temperature(C), and rainfall (mm).  Currently, it supports per year based prediction with a planting date for a single growing season for a single crop in a single simulation.  In addition to that, temperature values should not have missing values in the input. 
Management module: It defines the soli type, moisture level input, and prior irrigation. Also, various depths of the aquifer can be characterized through 'config' to support the modeling operation.

Calculation module [ GDU and PET module ]: The module calculates the aggregated growing degree day (GDU )values from planting and determines the evapotranspiration based on selected evapotranspiration equation. Currently, it supports three equations: Penman–Monteith Equation,  Priestley–Taylor, Blainy-Criddle Equation.
Recommendation module: It generates daily crop water use and provides a next week's recommendation based on forecast data. 

![PyPani Flow Diagram](Flowchart.jpg)

Installation Guide
---------
The package can be install as regular python package. 
The python version of the package: 3.8.2

To check python version:
```pip --version```

To install: 
```pip install git+https://github.com/malfihasan/PyPani.git#egg=PyPani```


Example Run
---------
To run manually:
``` python model.py 03/10/2018 322/2017```

To build and test the package.

```pip3 install -e . ```

Example data can be found in "tests" folder

Contact
---------
Dr. M. Alfi Hasan - mdalfihasan19@gmail.com - http://www.malfihasan.com/
Dr. Urs Christoph SCHULTHESS - U.Schulthess@cgiar.org 
Distributed under the MIT license. See LICENSE.txt for more information.


References
---------
[1] Collabortive partner:
-- The International Maize and Wheat Improvement Center (CIMMYT) in Bangladesh and Mexico
-- The Commonwealth Scientific and Industrial Research Organisation (CSIRO) in Australia
-- The International Crops Research Institute for the Semi-Arid Tropics (ICRISAT) in Mali and Nigeria
-- The University of Maryland, USA, in Tanzania and Uganda
-- M. Alfi Hasan - Independent consultant - Affiliated with the University of Rhode Island. 