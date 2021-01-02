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
    * config
        * resources
    * log
    * data
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

## config package
ConfigHolder – Manges config parameters used by simulation and ml packages

log – contains log files

data – contains *.csv data used by the simulation and ml packages


## Pairing Level Rules
* Pairing must start and end with same crew base.
* If a Pairing doesn't end in the base add deadhead to the base or add Layover leg
* FA TAFB (Time Away From Base) is considered
* FA minimum pay guarantee is considered
* Duty Level Rules
* Duty Period report time (brief time)can be 45 minutes domestic, 60 minutes international, 75 minutes international overwater before the flight departure time. Similarly release time (debrief) can be the same minutes after the flight arrival time.
* Minimum and maximum overnight rest between duties in a pairing.
* Maximum number of duties in a pairing.
* Maximum pairing length in calendar days.
* Duty period for FA Pairings can't exceed more than 18 hours
* The 8-in-24 rule, which requires a longer overnight rest time (compensatory rest) if there are more than 8 hours of flying time in any 24-hour window.
* Many more from government, labor union, and airline operational rules.
* If a duty period doesn't follow one of the rules add Layover

## Flight Level Rules
* Each flight will have minimum and maximum number of FAs based on flight duration
* Activity Builder – Build various activities for a given month

