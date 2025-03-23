# Authorization

## Source
https://developers.cloudflare.com/agents/model-context-protocol/authorization/

When building a [Model Context Protocol (MCP) ↗](https://modelcontextprotocol.io) server, you need both a way to allow users to login (authentication) and allow them to grant the MCP client access to resources on their account (authorization).
The Model Context Protocol uses [a subset of OAuth 2.1 for authorization ↗](https://spec.modelcontextprotocol.io/specification/draft/basic/authorization/). OAuth allows your users to grant limited access to resources, without them having to share API keys or other credentials.
Cloudflare provides an [OAuth Provider Library ↗](https://github.com/cloudflare/workers-oauth-provider) that implements the provider side of the OAuth 2.1 protocol, allowing you to easily add authorization to your MCP server.
You can use the OAuth Provider Library in three ways:
  1. **Your Worker handles authorization itself.** Your MCP server, running on Cloudflare, handles the complete OAuth flow. ([Example](https://developers.cloudflare.com/agents/guides/remote-mcp-server/))
  2. **Integrate directly with a third-party OAuth provider** , such as GitHub or Google.
  3. **Integrate with your own OAuth provider** , including authorization-as-a-service providers you might already rely on, such as Stytch and Auth0.


The following sections describe each of these options and link to runnable code examples for each.
## Authorization options
[](https://developers.cloudflare.com/agents/model-context-protocol/authorization/#authorization-options)
### (1) Your MCP Server handles authorization and authentication itself
[](https://developers.cloudflare.com/agents/model-context-protocol/authorization/#1-your-mcp-server-handles-authorization-and-authentication-itself)
Your MCP Server, using the [OAuth Provider Library ↗](https://github.com/cloudflare/workers-oauth-provider), can handle the complete OAuth authorization flow, without any third-party involvement.
The [Workers OAuth Provider Library ↗](https://github.com/cloudflare/workers-oauth-provider) is a Cloudflare Worker that implements a [`fetch()` handler](https://developers.cloudflare.com/workers/runtime-apis/handlers/fetch/), and handles incoming requests to your MCP server.
You provide your own handlers for your MCP Server's API, and autentication and authorization logic, and URI paths for the OAuth endpoints, as shown below:
```

exportdefaultnewOAuthProvider({
apiRoute:"/mcp",
// Your MCP server:
apiHandler:MyMCPServer.Router,
// Your handler for authentication and authorization:
defaultHandler:MyAuthHandler,
authorizeEndpoint:"/authorize",
tokenEndpoint:"/token",
clientRegistrationEndpoint:"/register",
});

```

Refer to the [getting started example](https://developers.cloudflare.com/agents/guides/remote-mcp-server/) for a complete example of the `OAuthProvider` in use, with a mock authentication flow.
The authorization flow in this case works like this:
```
MCP Server (your Worker)MCP ClientUser-Agent (Browser)MCP Server (your Worker)MCP ClientUser-Agent (Browser)Generate code_verifier and code_challengeUser logs in and authorizesBegin standard MCP message exchangeMCP RequestHTTP 401 UnauthorizedOpen browser with authorization URL + code_challengeGET /authorizeRedirect to callback URL with auth codeCallback with authorization codeToken Request with code + code_verifierAccess Token (+ Refresh Token)MCP Request with Access Token
```

Remember — [authentication is different from authorization ↗](https://www.cloudflare.com/learning/access-management/authn-vs-authz/). Your MCP Server can handle authorization itself, while still relying on an external authentication service to first authenticate users. The [example](https://developers.cloudflare.com/agents/guides/remote-mcp-server) in getting started provides a mock authentdcation flow. You will need to implement your own authentication handler — either handling authentication yourself, or using an external authentication services.
### (2) Third-party OAuth Provider
[](https://developers.cloudflare.com/agents/model-context-protocol/authorization/#2-third-party-oauth-provider)
The [OAuth Provider Library ↗](https://github.com/cloudflare/workers-oauth-provider) can be configured to use a third-party OAuth provider, such as GitHub or Google. You can see a complete example of this in the [GitHub example](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#add-authentication).
When you use a third-party OAuth provider, you must provide a handler to the `OAuthProvider` that implements the OAuth flow for the third-party provider.
```

import MyAuthHandler from "./auth-handler";
exportdefaultnewOAuthProvider({
apiRoute:"/mcp",
// Your MCP server:
apiHandler:MyMCPServer.Router,
// Replace this handler with your own handler for authentication and authorization with the third-party provider:
defaultHandler:MyAuthHandler,
authorizeEndpoint:"/authorize",
tokenEndpoint:"/token",
clientRegistrationEndpoint:"/register",
});

```

Note that as [defined in the Model Context Protocol specification ↗](https://spec.modelcontextprotocol.io/specification/draft/basic/authorization/#292-flow-description) when you use a third-party OAuth provider, the MCP Server (your Worker) generates and issues its own token to the MCP client:
```
Third-Party Auth ServerMCP Server (your Worker)MCP ClientUser-Agent (Browser)Third-Party Auth ServerMCP Server (your Worker)MCP ClientUser-Agent (Browser)User authorizesGenerate bound MCP tokenInitial OAuth RequestRedirect to Third-Party /authorizeAuthorization RequestRedirect to MCP Server callbackAuthorization codeExchange code for tokenThird-party access tokenRedirect to MCP Client callbackMCP authorization codeExchange code for tokenMCP access token
```

Read the docs for the [Workers oAuth Provider Library ↗](https://github.com/cloudflare/workers-oauth-provider) for more details.
### (3) Bring your own OAuth Provider
[](https://developers.cloudflare.com/agents/model-context-protocol/authorization/#3-bring-your-own-oauth-provider)
If your application already implements an Oauth Provider itself, or you use Stytch, Auth0, or authorization-as-a-service provider, you can use this in the same way that you would use a third-party OAuth provider, described above in (2).
## Next steps
[](https://developers.cloudflare.com/agents/model-context-protocol/authorization/#next-steps)
  * [Learn how to use the Workers OAuth Provider Library ↗](https://github.com/cloudflare/workers-oauth-provider)
  * Learn how to use a third-party OAuth provider, using the [GitHub](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#add-authentication) example MCP server.


## Was this helpful?
[ Edit page](https://github.com/cloudflare/cloudflare-docs/edit/production/src/content/docs/agents/model-context-protocol/authorization.mdx)
Last updated: Mar 20, 2025
[ Previous Model Context Protocol (MCP) ](https://developers.cloudflare.com/agents/model-context-protocol/) [ Next Tools ](https://developers.cloudflare.com/agents/model-context-protocol/tools/)
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




---

# Tools

## Source
https://developers.cloudflare.com/agents/model-context-protocol/tools/

Model Context Protocol (MCP) tools are functions that a [MCP Server](https://developers.cloudflare.com/agents/model-context-protocol) provides and MCP clients can call.
When you build MCP Servers with the `@cloudflare/model-context-protocol` package, you can define tools the [same way as shown in the `@modelcontextprotocol/typescript-sdk` package's examples ↗](https://github.com/modelcontextprotocol/typescript-sdk?tab=readme-ov-file#tools).
For example, the following code from [this example MCP server ↗](https://github.com/cloudflare/ai/tree/main/demos/remote-mcp-server) defines a simple MCP server that adds two numbers together:
  * [ JavaScript ](https://developers.cloudflare.com/agents/model-context-protocol/tools/#tab-panel-762)
  * [ TypeScript ](https://developers.cloudflare.com/agents/model-context-protocol/tools/#tab-panel-763)


```

import {McpServer} from "@modelcontextprotocol/sdk/server/mcp";
import {DurableMCP} from "@cloudflare/model-context-protocol";
exportclassMyMCPextendsDurableMCP{
server =newMcpServer({ name:"Demo", version:"1.0.0"});
asyncinit(){
this.server.tool(
"add",
{ a:z.number(), b:z.number() },
async({a,b})=> ({
content: [{ type:"text", text:String(a+b) }],
}),
);
}
}

```

```

import {McpServer} from "@modelcontextprotocol/sdk/server/mcp";
import {DurableMCP} from "@cloudflare/model-context-protocol";
exportclassMyMCPextendsDurableMCP{
server =newMcpServer({ name:"Demo", version:"1.0.0"});
asyncinit(){
this.server.tool(
"add",
{ a:z.number(), b:z.number() },
async({a,b})=> ({
content: [{ type:"text", text:String(a+b) }],
}),
);
}
}

```

## Was this helpful?
[ Edit page](https://github.com/cloudflare/cloudflare-docs/edit/production/src/content/docs/agents/model-context-protocol/tools.mdx)
Last updated: Mar 20, 2025
[ Previous Authorization ](https://developers.cloudflare.com/agents/model-context-protocol/authorization/) [ Next Transport ](https://developers.cloudflare.com/agents/model-context-protocol/transport/)
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




---

# Transport

## Source
https://developers.cloudflare.com/agents/model-context-protocol/transport/

The Model Context Protocol (MCP) specification defines [two standard transport mechanisms ↗](https://spec.modelcontextprotocol.io/specification/draft/basic/transports/):
  1. **stdio, communication over standard in and standard out** — designed for local MCP connections
  2. **HTTP with Server-Sent Events (SSE)** — designed for remote MCP connections


MCP Servers deployed to Cloudflare support remote MCP connections, using HTTP with Server-Sent Events (SSE) as transport. SSE requires a persistent HTTP connection, which is supported by Cloudflare [Durable Objects](https://developers.cloudflare.com/durable-objects/). Transport is configured and handled automatically. You don't need to configure anything — it just works.
Note
Even if the MCP client you are using only supports local MCP connections, you can still connect it to a remote MCP server.
Follow [this guide](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/) for instructions on how to connect to your remote MCP server from Claude Desktop, Cursor, Windsurf, and other local MCP clients, using the [`mcp-remote` local proxy ↗](https://www.npmjs.com/package/mcp-remote).
## Was this helpful?
[ Edit page](https://github.com/cloudflare/cloudflare-docs/edit/production/src/content/docs/agents/model-context-protocol/transport.mdx)
Last updated: Mar 20, 2025
[ Previous Tools ](https://developers.cloudflare.com/agents/model-context-protocol/tools/) [ Next Limits ](https://developers.cloudflare.com/agents/platform/limits/)
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




---

