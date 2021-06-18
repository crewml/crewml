# CrewML
CrewML is an open-source project developed in Python for optimizing airline crew 
pairing generation and assigning flight crew (Pilots and Flight Attendants) to the 
crew pairing using Supervised Machine Learning (ML) Algorithms. To use supervised 
ML, we need to have real pairing data used by commercial airlines. Unfortunately, 
all pairing data are copyrighted by respective airlines and not easy to obtain. 
To solve the data problem we decided to generate the pairing data from the 
commercial flight data obtained from Bureau of Transportation Statistics 
maintained by the United States Department of Transportation. Using the flight 
data we generated the Pairing and used it to create the ML models.



# Python Custom Packages
* crewml - Contains simulation and ml modules. simulation module contains packages to
  create pairings. ml module contains machine learning algorithm packages to 
  apply machine learning algorithms on the data generated from the simulation package.
   
* electric - Contains electric outage specific modules. It contains packages 
     to create JSON objects and XML messages. 
   
* tests - All unit tests that use pytest and moto (mock services for AWS). It also
     contains integration test units that start with int_test* which runs with various
     AWS services.
   
* resources - all config data
   
* log - contain log file
   
* data - contain various *.csv files

# Thirdparty Packages used
* numpy
* matplotlib
* scipy


### Project Structure
* crewml
    * simulation
        * pairing            
    * ml
        * visualizer
        * prreg
        * prlogreg
    * config
        * resources
    * log
    * data
        * download
        * feature
    * docs


![Data Flow](/image/crewml-dataflow.png)

# Design
## simul Package

Following are important modules of the simulation package:

FlightCleaner – Reads the commercial flight data, removes unnecessary data, and converts all the time to UTC.

FlightClassifer – Reads the cleaned flight data, classifies the flights based on crew base and non-base.

DutyGenerator – Uses the classified flights to create a duty for each flight which will be used to create the pairing.

PairingGenerator – Uses the duty to generate pairing for the flights.

CostCalculator – Calculates cost associated with each pairing.

## ml package
Following are the important modules of ml package:
visualizer - Contains various classes to plot graphs using seaborn
prlogreg - Pairing logistic Regression model
prreg - Pairing Regression model

## config package
ConfigHolder – Manges config parameters used by simulation and ml packages

log – contains log files

data – contains *.csv data used by the simulation and ml packages
download - A class that helps to download flight data from Amazon 
S3 and validates data with signature defined in the config file. 
feature - This class contains the data downloaded from S3.

## Pairing Level Rules
* Pairing must start and end with same crew base.
* If a Pairing doesn't end in the base add deadhead to the base or add Layover leg
* All Pairings will have duties attached with it. Each duty will have one or more flights

## Duty Level Rules
* 1. 45 minutes (brief time) added to flight departure time which will be duty period report time.
* 2. 45 minutes (dbrief time) added to flight arrival time which will be duty period end time.
* 3. A duty can have one or more flights attached to it. duty period end time is the last flight's
* arrival time + 45
* 4. Within each duty two consecutive flights are seperated by 15 minutes, sit-time. For the 
* duty period total time calculations, 15 minutes is substracted from the each flight's departure time
* and 15 minutes is added to flight arrival time.
* 5. Total duty period within a pairing is between 8-12 hours
* 6. Layover added for the flight at the end of the duty if the duty ends not 
* in staring base origin airport and if the flight arrival time falls between 8PM and 6AM.

## Flight Level Rules
* 1. A flight has one departure and one arrival airport in it.

