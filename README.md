# Traze : A Real-Time Routing, Scheduling, and Monitoring Android Application for Delivery Services using Dijkstra Algorithm and Ant Colony Optimization

Welcome to the Traze GitHub repository! Traze is an advanced delivery system designed to address the growing demands and challenges in the global parcel delivery market. With the total number of parcels expected to exceed 260 billion by 2026, Traze aims to improve delivery services by shortening routes, ensuring goods safety, and reducing operational costs.

The system utilizes a combination of the Dijkstra and Ant Colony Optimization (ACO) algorithms to find the optimal routes for deliveries. In addition to route optimization, Traze incorporates scheduling functionality to prioritize perishable goods and prevent damage. Customers can track their deliveries using assigned tracking numbers, providing transparency and reducing hassle for both delivery personnel and customers. With features like scheduling, tracking, and transparency, Traze meets customer demands while providing competitive advantages for delivery service providers.

This study aims to develop an effective and reliable logistics system capable of scheduling, and monitoring deliveries.
1. Initializing the Dijkstra algorithm to determine the optimal route and integrating Ant Colony Optimization (ACO) algorithm for alternative routes.
2. Develop a delivery services android application  with real-time routing, scheduling and monitoring.
3. Evaluate the mobile application implementation using ISO 25010:2011.

Each one of the objectives were successfully achieved and tackled.



<h2>App Installation Process</h2>
  
  1. Download Traze (".apk") in the **[dist folder](https://github.com/Mariaarlyn14/Traze/blob/main/dist/Traze.apk)** or using this **[link](https://drive.google.com/file/d/1JDvw4AGQyV0Vh0qQLcl3jGebb22NVf2T/view?usp=share_link)**.
  2. Install the Traze Application in your **Android** device.
  3. Go the **"App info"** and make sure to turn on the **Permission for Files and Media**.
  4. Use the app

Setting Up the Algorithm
-----
1. Install python IDE and python3.
2. Install the libraries needed by the algorithm to run.

      >Use pip install -r [requirements.txt](https://github.com/Mariaarlyn14/Traze/blob/main/requirements.txt) in the command line.
      
3. Download the database [("test2.db")](https://github.com/Mariaarlyn14/Traze/blob/main/db/DataLocation.db) to access the necessary Data for the algorithm to work.
4. Run the algorithm.
5. Upon executing the code, you will obtain two HTML files, namely "Dijkstra.html" and "ACO.html". These files can be conveniently downloaded and stored on your mobile device to use for the application.


Make use of this [Google Collab Python Notebook](https://colab.research.google.com/drive/1dSIbjAXhbsRaO5O8azrfq-hAqGfk0whj?usp=sharing), created with the intention of improving the efficiency and ease of running algorithms for our users.


Folders
---

/assets - contains Logo of the Android Application.</br>
/db - contains the Location database needed for the algorithm.</br>
/dist - contains the Android Application.</br>
/src - contains the source code for both Backend and Frontend.</br>
