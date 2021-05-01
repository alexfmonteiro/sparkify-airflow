# Sparkify Airflow: Data Pipelines with Airflow

This project creates a ETL pipeline written in Python to process two different datasets, logs and songs, and load them into Redshift with tables designed to optimize queries on song play analysis. 

Firtly, the ETL pulls data from an S3 bucket and loads it to staging tables on Redshift, then, it executes SQL statements that create the analytics tables from these staging tables.

Apache Airflow is used to orchestrate every task.

## Datasets

### Song Dataset
The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset.

`song_data/A/B/C/TRABCEI128F424C983.json`

`song_data/A/A/B/TRAABJL12903CDCF1A.json`

And below is an example of what a single song file, `TRAABJL12903CDCF1A.json`, looks like.

```javascript
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}
```

### Log Dataset
The second dataset consists of log files in JSON format generated by this event simulator based on the songs in the dataset above. These simulate activity logs from a music streaming app based on specified configurations.

The log files in the dataset you'll be working with are partitioned by year and month. For example, here are filepaths to two files in this dataset.

`log_data/2018/11/2018-11-12-events.json`

`log_data/2018/11/2018-11-13-events.json`

And below is an example of what the data in a log file, `2018-11-12-events.json`, looks like (just the first 5 rows).

```javascript
{"artist":null,"auth":"Logged In","firstName":"Celeste","gender":"F","itemInSession":0,"lastName":"Williams","length":null,"level":"free","location":"Klamath Falls, OR","method":"GET","page":"Home","registration":1541077528796.0,"sessionId":438,"song":null,"status":200,"ts":1541990217796,"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/37.0.2062.103 Safari\/537.36\"","userId":"53"}
{"artist":"Pavement","auth":"Logged In","firstName":"Sylvie","gender":"F","itemInSession":0,"lastName":"Cruz","length":99.16036,"level":"free","location":"Washington-Arlington-Alexandria, DC-VA-MD-WV","method":"PUT","page":"NextSong","registration":1540266185796.0,"sessionId":345,"song":"Mercy:The Laundromat","status":200,"ts":1541990258796,"userAgent":"\"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit\/537.77.4 (KHTML, like Gecko) Version\/7.0.5 Safari\/537.77.4\"","userId":"10"}
{"artist":"Barry Tuckwell\/Academy of St Martin-in-the-Fields\/Sir Neville Marriner","auth":"Logged In","firstName":"Celeste","gender":"F","itemInSession":1,"lastName":"Williams","length":277.15873,"level":"free","location":"Klamath Falls, OR","method":"PUT","page":"NextSong","registration":1541077528796.0,"sessionId":438,"song":"Horn Concerto No. 4 in E flat K495: II. Romance (Andante cantabile)","status":200,"ts":1541990264796,"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/37.0.2062.103 Safari\/537.36\"","userId":"53"}
{"artist":"Gary Allan","auth":"Logged In","firstName":"Celeste","gender":"F","itemInSession":2,"lastName":"Williams","length":211.22567,"level":"free","location":"Klamath Falls, OR","method":"PUT","page":"NextSong","registration":1541077528796.0,"sessionId":438,"song":"Nothing On But The Radio","status":200,"ts":1541990541796,"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/37.0.2062.103 Safari\/537.36\"","userId":"53"}
{"artist":null,"auth":"Logged In","firstName":"Jacqueline","gender":"F","itemInSession":0,"lastName":"Lynch","length":null,"level":"paid","location":"Atlanta-Sandy Springs-Roswell, GA","method":"GET","page":"Home","registration":1540223723796.0,"sessionId":389,"song":null,"status":200,"ts":1541990714796,"userAgent":"\"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit\/537.78.2 (KHTML, like Gecko) Version\/7.0.6 Safari\/537.78.2\"","userId":"29"}
```

## Database

![Entity-Relatioship Diagram](https://github.com/alexfmonteiro/sparkify-redshift/blob/main/sparkifydb_erd.png)

The Redshift tables were designed to optimize queries on song play analysis. 

To achieve that, it was created two staging tables to receive the logs and the songs data via bulk inserts using the PostgreSQL `copy` command:

#### Staging Tables
 1. **staging_events** - records in log data files
    - artist, auth, firstName, gender, itemInSession, lastName, length, level, location, method, page, registration, sessionId, song, status, ts, userAgent, userId
 2. **staging_songs** - records in song data files
    - num_songs, artist_id, artist_latitude, artist_longitude, artist_location, artist_name, song_id, title, duration, year


Also, it was created a  star schema including the following tables:

#### Fact Table
 1. **songplays** - records in log data associated with song plays i.e. records with page NextSong
    - songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

#### Dimension Tables
 2. **users** - users in the app
    - *user_id, first_name, last_name, gender, level*
 3. **songs** - songs in music database
    - *song_id, title, artist_id, year, duration*
 4. **artists** - artists in music database
    - *artist_id, name, location, latitude, longitude*
 5. **time** - timestamps of records in songplays broken down into specific units
    - *start_time, hour, day, week, month, year, weekday*

## Airflow 
The following DAG (Direct Acyclic Graph) was built:

![DAG](https://github.com/alexfmonteiro/sparkify-airflow/blob/main/images/dag.png)


### Prerequisites

In order to run this ETL, an instance of Apache Airflow 1.10.x needs to be up and running.

Also, Airflow needs to have the following connections configured:
 - A connection called `redshift_conn` of type PostgreSQL specifying a Redshift valid cluster.
 - A connection called `s3_conn` of type S3 specifying valid AWS credentials with privileges to create tables in Redshift.




