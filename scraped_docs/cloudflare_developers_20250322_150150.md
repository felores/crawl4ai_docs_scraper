# Build a remote MCP server

## Source
https://developers.cloudflare.com/agents/guides/remote-mcp-server/

## Deploy your first MCP server
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#deploy-your-first-mcp-server)
This guide will walk you through how to deploy an [example MCP server ↗](https://github.com/cloudflare/ai/tree/main/demos/remote-mcp-server) to your Cloudflare account. You will then customize this example to suit your needs.
To get started, run the following command to create a new MCP server:
  * [ npm ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#tab-panel-764)
  * [ pnpm ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#tab-panel-765)
  * [ yarn ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#tab-panel-766)


Terminal window```

npmcreatecloudflare@latest--my-mcp-server--template=cloudflare/ai/demos/remote-mcp-server

```

Terminal window```

pnpmcreatecloudflare@latestmy-mcp-server--template=cloudflare/ai/demos/remote-mcp-server

```

Terminal window```

yarncreatecloudflaremy-mcp-server--template=cloudflare/ai/demos/remote-mcp-server

```

Now, you have the MCP server setup, with dependencies installed. Move into that project folder:
Terminal window```

cdmy-mcp-server

```

### Local development
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#local-development)
In the directory of your new project, run the following command to start the development server:
Terminal window```

npmstart

```

Your MCP server is now running on `http://localhost:8787/sse`.
In a new terminal, run the [MCP inspector ↗](https://github.com/modelcontextprotocol/mcp-inspector). The MCP inspector is an interactive MCP client that allows you to connect to your MCP server and invoke tools from a web browser.
Terminal window```

npx@modelcontextprotocol/inspector@latest

```

Open the MCP inspector in your web browser:
Terminal window```

openhttp://localhost:5173

```

In the inspector, enter the URL of your MCP server, `http://localhost:8787/sse`, and click **Connect** :
![MCP inspector — where to enter the URL of your MCP server](https://developers.cloudflare.com/_astro/mcp-inspector-enter-url.Chu-Nz-A_Z2xJ68.webp)
You will be redirected to an example OAuth login page. Enter any username and password and click "Log in and approve" to continue. (you can add your own authentication and/or authorization provider to replace this. Refer to the [authorization](https://developers.cloudflare.com/agents/model-context-protocol/authorization/) section for details on how to do this.)
![MCP OAuth Login Page](https://developers.cloudflare.com/_astro/mcp-demo-oauth-flow.DS52IPPI_Z1y2MYK.webp)
Once you have logged in, you will be redirected back to the inspector. You should see the "List Tools" button, which will list the tools that your MCP server exposes.
![MCP inspector — authenticated](https://developers.cloudflare.com/_astro/mcp-inspector-authenticated.BCabYwDA_ezC3N.webp)
### Deploy your MCP server
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#deploy-your-mcp-server)
You can deploy your MCP server to Cloudflare using the following [Wrangler CLI command](https://developers.cloudflare.com/workers/wrangler) within the example project:
Terminal window```

npxwrangler@latestdeploy

```

If you have already [connected a git repository](https://developers.cloudflare.com/workers/ci-cd/builds/) to the Worker with your MCP server, you can deploy your MCP server by pushing a change or merging a pull request to the main branch of the repository.
After deploying, take the URL of your deployed MCP server, and enter it in the MCP inspector running on `http://localhost:5173`. You now have a remote MCP server, deployed to Cloudflare, that MCP clients can connect to.
### Connect your remote MCP server to Claude and other MCP Clients via a local proxy
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#connect-your-remote-mcp-server-to-claude-and-other-mcp-clients-via-a-local-proxy)
Now that your MCP server is running with OAuth authentication, you can use the [`mcp-remote` local proxy ↗](https://www.npmjs.com/package/mcp-remote) to connect Claude Desktop or other MCP clients to it — even though these tools aren't yet _remote_ MCP clients, and don't support remote transport or authorization on the client side. This lets you to test what an interaction with your OAuth-enabled MCP server will be like with a real MCP client.
Update your Claude Desktop configuration to point to the URL of your MCP server. You can use either the `localhost:8787/sse` URL, or the URL of your deployed MCP server:
```

{
"mcpServers":{
"math":{
"command":"npx",
"args":[
"mcp-remote",
"https://your-worker-name.your-account.workers.dev/sse"
]
}
}
}

```

Restart Claude Desktop and complete the authentication flow again. Once this is done, Claude will be able to make calls to your remote MCP server. you can test this by asking Claude to use one of your tools. For example: "Could you use the math tool to add 23 and 19?". Claude should invoke the tool and show the result generated by the MCP server.
Learn more about other ways of using remote MCP servers with MCP clients here in [this section](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server).
## Add Authentication
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#add-authentication)
The example MCP server you just deployed above acts as an OAuth provider to MCP clients, handling authorization, but has a placeholder authentication flow. It lets you enter any username and password to log in, and doesn't actually authenticate you against any user database.
In the next section, you will add a real authentication provider to your MCP server. Following these steps will show you more clearly how to integrate it with your MCP server. We'll use GitHub in this example, but you can use any OAuth provider that supports the OAuth 2.0 specification, including Google, Slack, Stytch, Auth0, and more.
### Step 1 — Create and deploy a new MCP server
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#step-1--create-and-deploy-a-new-mcp-server)
Run the following command to create a new MCP server:
  * [ npm ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#tab-panel-767)
  * [ pnpm ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#tab-panel-768)
  * [ yarn ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#tab-panel-769)


Terminal window```

npmcreatecloudflare@latest--my-mcp-server-github-auth--template=cloudflare/ai/demos/remote-mcp-github-oauth

```

Terminal window```

pnpmcreatecloudflare@latestmy-mcp-server-github-auth--template=cloudflare/ai/demos/remote-mcp-github-oauth

```

Terminal window```

yarncreatecloudflaremy-mcp-server-github-auth--template=cloudflare/ai/demos/remote-mcp-github-oauth

```

Now, you have the MCP server setup, with dependencies installed. Move into that project folder:
Terminal window```

cdmy-mcp-server-github-auth

```

Then, run the following command to deploy the MCP server:
Terminal window```

npxwrangler@latestdeploy

```

You'll notice that in the example MCP server, if you open `src/index.ts`, the primary difference is that the `defaultHandler` is set to the `GitHubHandler`:
```

import GitHubHandler from "./github-handler";
exportdefaultnewOAuthProvider({
apiRoute:"/sse",
apiHandler:MyMCP.Router,
defaultHandler:GitHubHandler,
authorizeEndpoint:"/authorize",
tokenEndpoint:"/token",
clientRegistrationEndpoint:"/register",
});

```

This will ensure that your users are redirected to GitHub to authenticate. To get this working though, you need to create OAuth client apps in the steps below.
### Step 2 — Create an OAuth App
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#step-2--create-an-oauth-app)
You'll need to create two [GitHub OAuth Apps ↗](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) to use GitHub as an authentication provider for your MCP server — one for local development, and one for production.
#### First create a new OAuth App for local development
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#first-create-a-new-oauth-app-for-local-development)
Navigate to [github.com/settings/developers ↗](https://github.com/settings/developers) to create a new OAuth App with the following settings:
  * **Application name** : `My MCP Server (local)`
  * **Homepage URL** : `http://localhost:8787`
  * **Authorization callback URL** : `http://localhost:8787/callback`


For the OAuth app you just created, add the client ID of the OAuth app as `GITHUB_CLIENT_ID` and generate a client secret, adding it as `GITHUB_CLIENT_SECRET` to a `.dev.vars` file in the root of your project, which [will be used to set secrets in local development](https://developers.cloudflare.com/workers/configuration/secrets/).
Terminal window```

touch.dev.vars
echo'GITHUB_CLIENT_ID="your-client-id"'>>.dev.vars
echo'GITHUB_CLIENT_SECRET="your-client-secret"'>>.dev.vars
cat.dev.vars

```

#### Next, run your MCP server locally
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#next-run-your-mcp-server-locally)
Run the following command to start the development server:
Terminal window```

npmstart

```

Your MCP server is now running on `http://localhost:8787/sse`.
In a new terminal, run the [MCP inspector ↗](https://github.com/modelcontextprotocol/mcp-inspector). The MCP inspector is an interactive MCP client that allows you to connect to your MCP server and invoke tools from a web browser.
Terminal window```

npx@modelcontextprotocol/inspector@latest

```

Open the MCP inspector in your web browser:
Terminal window```

openhttp://localhost:5173

```

In the inspector, enter the URL of your MCP server, `http://localhost:8787/sse`, and click **Connect** :
You should be redirected to a GitHub login or authorization page. After authorizing the MCP Client (the inspector) access to your GitHub account, you will be redirected back to the inspector. You should see the "List Tools" button, which will list the tools that your MCP server exposes.
#### Second — create a new OAuth App for production
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#second-create-a-new-oauth-app-for-production)
You'll need to repeat these steps to create a new OAuth App for production.
Navigate to [github.com/settings/developers ↗](https://github.com/settings/developers) to create a new OAuth App with the following settings:
  * **Application name** : `My MCP Server (production)`
  * **Homepage URL** : Enter the workers.dev URL of your deployed MCP server (ex: `worker-name.account-name.workers.dev`)
  * **Authorization callback URL** : Enter the `/callback` path of the workers.dev URL of your deployed MCP server (ex: `worker-name.account-name.workers.dev/callback`)


For the OAuth app you just created, add the client ID and client secret, using Wrangler CLI:
Terminal window```

wranglersecretputGITHUB_CLIENT_ID

```

Terminal window```

wranglersecretputGITHUB_CLIENT_SECRET

```

#### Finally, connect to your MCP server
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#finally-connect-to-your-mcp-server)
Now that you've added the ID and secret of your production OAuth app, you should now be able to connect to your MCP server running at `worker-name.account-name.workers.dev/sse` using the MCP inspector or ([other MCP clients](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#connect-your-mcp-server-to-claude-and-other-mcp-clients)), and authenticate with GitHub.
## Next steps
[](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#next-steps)
  * Add [tools](https://developers.cloudflare.com/agents/model-context-protocol/tools/) to your MCP server.
  * Customize your MCP Server's [authentication and authorization](https://developers.cloudflare.com/agents/model-context-protocol/authorization/).


## Was this helpful?
[ Edit page](https://github.com/cloudflare/cloudflare-docs/edit/production/src/content/docs/agents/guides/remote-mcp-server.mdx)
Last updated: Mar 21, 2025
[ Previous Implement Effective Agent Patterns ↗ ](https://github.com/cloudflare/agents/tree/main/guides/anthropic-patterns) [ Next Test a Remote MCP Server ](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/)
  * **Resources**
  * [ API ](https://developers.cloudflare.com/api/)
  * [ New to Cloudflare? ](https://developers.cloudflare.com/fundamentals/)
  * [ Products ](https://developers.cloudflare.com/products/)
  * [ Sponsorships ](https://developers.cloudflare.com/sponsorships/)
  * [ Open Source ](https://github.com/cloudflare)


  * **Support**
  * [ Help Center ](https://support.cloudflare.com/)
  * [ System Status ](https://www.cloudflarestatus.com/)
  * [ Compliance ](https://www.cloudflare.com/trust-hub/compliance-resources/)
  * [ GDPR ](https://www.cloudflare.com/trust-hub/gdpr/)


  * **Company**
  * [ cloudflare.com ](https://www.cloudflare.com/)
  * [ Our team ](https://www.cloudflare.com/people/)
  * [ Careers ](https://www.cloudflare.com/careers/)


  * **Tools**
  * [ Cloudflare Radar ](https://radar.cloudflare.com/)
  * [ Speed Test ](https://speed.cloudflare.com/)
  * [ Is BGP Safe Yet? ](https://isbgpsafeyet.com/)
  * [ RPKI Toolkit ](https://rpki.cloudflare.com/)
  * [ Certificate Transparency ](https://ct.cloudflare.com/)


  * **Community**
  * [ X ](https://x.com/cloudflare)
  * [ Discord ](http://discord.cloudflare.com/)
  * [ YouTube ](https://www.youtube.com/cloudflare)
  * [ GitHub ](https://github.com/cloudflare/cloudflare-docs)


  * 2025 Cloudflare, Inc.
  * [ Privacy Policy ](https://www.cloudflare.com/privacypolicy/)
  * [ Terms of Use ](https://www.cloudflare.com/website-terms/)
  * [ Report Security Issues ](https://www.cloudflare.com/disclosure/)
  * [ Trademark ](https://www.cloudflare.com/trademark/)
  * Cookie Settings