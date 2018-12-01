===================================================================
   ____   ____   _____
  / __ \ / __ \ / ____|
 | |  | | |  | | (___
 | |  | | |  | |\___ \
 | |__| | |__| |____) |
  \___\_\\____/|_____/

  _   _ ______ _________          ______  _____  _  __ _____
 | \ | |  ____|__   __\ \        / / __ \|  __ \| |/ // ____|
 |  \| | |__     | |   \ \  /\  / | |  | | |__) | ' /| (___
 | . ` |  __|    | |    \ \/  \/ /| |  | |  _  /|  <  \___ \
 | |\  | |____   | |     \  /\  / | |__| | | \ \| . \ ____) |
 |_| \_|______|  |_|      \/  \/   \____/|_|  \_|_|\_|_____/

==================================================================


ServiceNow Activation Integration v1.0:
------------------------------------------------------------------

**serialInput.py**

Development Environment: Python 3.7.2
Created: November 2018
By: Brendan Tung

USAGE:
- python3 serialInput.py

FUNCTION:
- This application serves as an add-on to the "manual-activation.py" script used in Activation Manager created by August Gross

- Capabilities:
    - Verify configuration item status and current company in ServiceNow 
    - Assign valid configuration item to existing, matching company provisioning tasks in ServiceNow
    - Changes provisioning task state from Open to Close

REQUIREMENTS:
- Json file retrieved from manual-activation.py
    - Format: {"Company":company_name,"Serial_Number":[{"SN":serial_number1},{"SN":serial_number2},...]}
    - If Json file is not retrieved from manual-activation.py
        - Modify local json file "testJson.json" to run script in aforementioned format

- ServiceNow 
    - All Serial Numbers that are scanned exist in ServiceNow
    - All Serial Numbers need to be assigned to the proper company
    - All Serial Numbers have the status "In Stock"
    - All Company locations have an Open Provisioning task

------------------------------------------------------------------

**testJson.json**

Development Environment: Json File
Created: November 2018
By: Brendan Tung

USAGE:
    - Provide Company and Serial Number mapping for data input in serialInput.py
    - serialInput.py functionality mentioned above 

REQUIREMENTS:
- Information retrieval
    - Obtained from manual-activation.py

------------------------------------------------------------------
