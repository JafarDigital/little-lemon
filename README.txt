To test the API easily, follow these steps:

Import the Postman test suite:

    -> Open Postman
    -> click Import (top left)
    -> choose Upload Files
    -> select the littlelemon_api_tests.json file included
    -> Click Import

In case you have to send up new environment in Postman: 
   -> Navigate to "Environments" in left sidebar (or: top right corner)
   -> Click + [i.e. add new environment]
   -> Set an environment variable named "base_url" with values http://127.0.0.1:8000
   -> Set an environment variable named "token" -- here you will assign the tokins from login

User "jafar" is admin and the password is "5"
The passwords of all other users is "c12345678"
User "bedouin" is manager
User "bambini" should be delivery crew

Since I couldn't manage to automatically assign tokens for postman test suite:

  -> whenever you login to any user you should copy their token
  -> then navigate to the environment
  -> change variable token's current value to the token you copied
  -> continue testing

I tested everything and it worked on my end, except I’m not sure if pagination is working as expected

Apologies in advance if anything breaks!!
