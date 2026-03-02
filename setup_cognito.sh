#!/bin/bash
export REGION=us-east-1
export USERNAME=testuser
export PASSWORD=TestPass123!

export POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "FisMcpPool" \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region $REGION | jq -r '.UserPool.Id')

export CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "FisMcpClient" \
  --no-generate-secret \
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region $REGION | jq -r '.UserPoolClient.ClientId')

aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username $USERNAME \
  --region $REGION \
  --message-action SUPPRESS > /dev/null

aws cognito-idp admin-set-user-password \
  --user-pool-id $POOL_ID \
  --username $USERNAME \
  --password $PASSWORD \
  --region $REGION \
  --permanent > /dev/null

export BEARER_TOKEN=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=$USERNAME,PASSWORD=$PASSWORD \
  --region $REGION | jq -r '.AuthenticationResult.AccessToken')

echo "Discovery URL: https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
echo "Client ID: $CLIENT_ID"
echo ""
echo "export BEARER_TOKEN='$BEARER_TOKEN'"
