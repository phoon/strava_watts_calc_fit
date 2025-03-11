# strava_watts_calc_fit
Convert strava analysis watts_calc data into a new fit file, so you can hold watts data in your fit file without a powermeter!

## Dependencies
```bash
pip install fit-tool pytz requests python-dotenv
```
## Usage
1. Create a api application on your strava setting page
2. Get a access token with scope activity:read_all 

    Open `http://www.strava.com/oauth/authorize?client_id={YOUR_CLIENT_ID}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all` with {YOUR_CLIENT_ID} in the browser. It will redirect to a url like `http://localhost/exchange_token?state=&code=2c043efb4c98176a6db78abd86a86b8a&scope=read,activity:read_all`,
    the `code` parameter is what we want.
3. Get access token from the output
```bash
curl -X POST https://www.strava.com/oauth/token \
-F client_id={YOUR_CLIENT_ID}\
-F client_secret={YOUR_CLIENT_SECRET} \
-F code={CODE} \
-F grant_type=authorization_code
```
4. Fill the ACCESS_TOKEN config in .env
5. Run the script!
```bash
python write_fit.py ACTIVITY_ID
```