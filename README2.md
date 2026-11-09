Create a `.env` file in the root of the project with the following environment variables. See:

```env
# Application ID

    
          
            
    

          
          Expand Down
    
    
  
GITHUB_APP_ID=123456
# Path to the App private key
GITHUB_APP_KEY_PATH=./config/key.pem
# or use the private key directly
GITHUB_APP_KEY=-----BEGIN PRIVATE KEY-----\n...
# Webhook Secret
GITHUB_APP_SECRET=123456789012345678901234567890
GITHUB_APP_ENDPOINT=/
GITHUB_GHAS_TEAM="sec_team"
# GHAS Severities
GITHUB_GHAS_SEVERITIES="critical,high,error,errors"
```
