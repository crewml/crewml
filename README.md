About the Project
This open source project is to use the flights to create Pairings, assign Pilots and Flight Attendants (FAs) to Pairing/Activity and create Schedule. Develop a Legality Rule Engine to identify if a Pilot or FA is legal to be part of Schedule or not. Simulate flight operations and make change to the schedule. For each change in Schedule check if the Pilot or FA is legal to be in the schedule or not. Store all the data used in the schedule and label if it passed legality or not. Use the generated labeled data to develop a machine learning model to predict if a Pilot or FA is legal to be in the Schedule or not without using the Legality Rule Engine.

Short-term Goals
Create Python packages with simple rules, create schedule, run simulation and collect data. Use the collected data to run Machine learning to predict the legality of FA/Pilot.
Design the packages in such a way it can grow on its own to create an ecosystem of components that can help flight crew domain. (Separate Schedule building, Simulation, and ML in its own package)
Long-term Goals
Grow the open source community and add more features to the package.
Get funding and host conference/user groups to educate others about the project.
Functional Requirements
Use the flight data to create Pairings for a month for a given carrier code (DL, UA, etc.)
Create separate Pairings for Pilots and FAs.
Based on the carrier, identify number of Pilots FAs working for that carrier and use the information to assign the Pairing.
Use the Pairing rules to build the Pairings
Use the Activity rules to build the activities.
Use Pairing and Activity rules to create Schedule for Employees
Use simulation components to simulate flight operations, and FA/Pilot life changes like Sick, Injury etc., to change the Schedule, check legality and store the result. Store all the data that are used to identify if FA/Pilot is legal. These labeled data will be used to develop the ML Model.
Design
Following are individual components that can be designed and developed independently.

Build Components
Following components are used to build the Pairings for a given month, carrier, flights, etc.

Pairing Builder – For a given set of flights, carrier, number of employees, build Pilot and FA Pairings to cover all the flights. Pairing Builder uses Pairing rule engine to build the Pairings. Pairing Builder is pluggable component, that can be changed based on different set of rules.

Pairing Rule Engine – Set of rules used to build the Pairings.There are three categories of rules, Pairing level rules, Duty level rules, and flight level rules.

Pairing Level Rules
Pairing must start and end with same crew base.
If a Pairing doesn't end in the base add deadhead to the base or add Layover leg
FA TAFB (Time Away From Base) is considered
FA minimum pay guarantee is considered
Duty Level Rules
Duty Period report time (brief time)can be 45 minutes domestic, 60 minutes international, 75 minutes international overwater before the flight departure time. Similarly release time (debrief) can be the same minutes after the flight arrival time.
Minimum and maximum overnight rest between duties in a pairing.
Maximum number of duties in a pairing.
Maximum pairing length in calendar days.
Duty period for FA Pairings can't exceed more than 18 hours
The 8-in-24 rule, which requires a longer overnight rest time (compensatory rest) if there are more than 8 hours of flying time in any 24-hour window.
Many more from government, labor union, and airline operational rules.
If a duty period doesn't follow one of the rules add Layover
Flight Level Rules
Each flight will have minimum and maximum number of FAs based on flight duration
Activity Builder – Build various activities for a given month

Activity Rule Engine – Set of rules used to build Activities. Rules are read from a text file.

Assignment Components
Pairing Assignment Rule Engine – Set of rules used to assign Pilots and FAs to Pairings. Activity Assignment Rule Engine – Set of rules used to assign activities to employees. Schedule Builder– Uses Pairing Assignment Rules and Activity Assignment Rules to create Pilot and FA Schedule.

All the above components are used to build Pilot and FA schedule for a given month.

Data Components
Data Access Component – Stores the data into S3, RDBMS, etc.

Legality Rule Components
FA Legality Rule Engine – Implement FAA rules, these rules are used to check the legality of FA and tells if an FA is valid to be on a Pairing or not. Pilot Legality Rule Engine – Implement FAA rules, these rules are used to check the legality of Pilot and tells if a Pilot is valid to be on a Pairing or not.

Simulation Components
These components run the simulation that are used to simulate real-world operational behavior of flights (delay, cancel, etc.) and Pilots/FAs life (sick, on job injury, late arrival, etc.) assigned to Schedule. Flight Operation Simulator – It uses the on-time arrival, various delay data from the flights and uses it to simulate flight operation like flight departing and arriving at the correct time, delay, etc. Pilot Life Simulator – This component simulates day-today life of a Pilot that can be used to simulate changes in Pilot schedule that can be used to check the legality of the pilot. FA Life Simulator - This component simulates day-today life of a FA that can be used to simulate changes in FA schedule. This can be used to check the legality of the FA. Schedule Manager – Starts the simulation components, based on simulation component response changes the Schedule, performs legality check and uses DB to store the result.

Component Interactions & Processing Steps
For a given Flights, Pairing Builder builds Pairings and Activity Builder builds activities using Pairing and Activity Rule Engine components.
Using Data Access Component store the Pairings and Activities.
Schedule Builder uses Pairing and Activity Assignment Rule components and creates Pilot/FA schedules
 Scheduler Manager starts the simulation components, make changes to  Pilot/FA schedules, run Legality Rules, and uses Data Access components to store the schedule along with the schedule is legally valid or not.
Other Requirements/Ideas
Use Python for developing the framework and application
Name of the project flightCrewPy, we’ll use standard Python libraries like numphy, pandas, etc., to create an ecosystem of all the components that are needed for flight crew domain.
For ML we can use any ML tools like scikit learn, tensorflow, etc.
We’ll separate data generation through simulation and ML model building in two separate packages so that both can be developed independently.
Each of the above component in the design should be in its own package and can be developed independently. This also helps individual component to grow independently without affecting all other components.
We’re not building the transactional application. We can use AWS S3 and EC2, without any RDBMS. We can store all the data in S3 and use EC2 for CPU. EC2 will be used to simulate and collect data for Machine Learning (ML) model. For ML training, we can either use EC2 or use AWS SageMaker or some other platform. RDBMS in cloud is expensive and we can avoid using it. Instead of EC2 we can also use AWS Lamda service to reduce cost.
For the rule components, it can be simple, declarative style specified in a text file. Individual components can read and use it. To start with we can have simple rules and over a period we can keep adding more rules.
Create domain objects for Pairing, Flight Schedule, etc.
Create Data access package so that it can read from any data source like S3, RDBMS etc.
Use automated testing tools to test the code automatically
References
Flight data from US Bureau of Transportation Statistics, https://www.transtats.bts.gov/DL_SelectFields.asp
Consideration of Passenger Interactions for the Prediction of Aircraft Boarding Time, https://pdfs.semanticscholar.org/ae0a/5bc5bdf44ccd54ac281da445f56b02f626ab.pdf


