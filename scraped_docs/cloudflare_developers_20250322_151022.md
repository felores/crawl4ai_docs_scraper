# Test a Remote MCP Server

## Source
https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/

Remote, authorized connections are an evolving part of the [Model Context Protocol (MCP) specification ↗](https://spec.modelcontextprotocol.io/specification/draft/basic/authorization/). Not all MCP clients support remote connections yet.
This guide will show you options for how to start using your remote MCP server with MCP clients that support remote connections. If you haven't yet created and deployed a remote MCP server, you should follow the [Build a Remote MCP Server](https://developers.cloudflare.com/agents/guides/remote-mcp-server/) guide first.
## The Model Context Protocol (MCP) inspector
[](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/#the-model-context-protocol-mcp-inspector)
The [`@modelcontextprotocol/inspector` package ↗](https://github.com/modelcontextprotocol/inspector) is a visual testing tool for MCP servers.
You can run it locally by running the following command:
Terminal window```

npx@modelcontextprotocol/inspector

```

Then, enter the URL of your remote MCP server. You can use an MCP server running on your local machine on localhost, or you can use a remote MCP server running on Cloudflare.
![MCP inspector](https://developers.cloudflare.com/_astro/mcp-inspector-enter-url.Chu-Nz-A_Z2xJ68.webp)
Once you have authenticated, you will be redirected back to the inspector. You should see the "List Tools" button, which will list the tools that your MCP server exposes.
![MCP inspector — authenticated](https://developers.cloudflare.com/_astro/mcp-inspector-authenticated.BCabYwDA_ezC3N.webp)
## Connect your remote MCP server to Claude Desktop via a local proxy
[](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/#connect-your-remote-mcp-server-to-claude-desktop-via-a-local-proxy)
Even though [Claude Desktop ↗](https://claude.ai/download) doesn't yet support remote MCP clients, you can use the [`mcp-remote` local proxy ↗](https://www.npmjs.com/package/mcp-remote) to connect it to your remote MCP server. This lets you to test what an interaction with your remote MCP server will be like with a real-world MCP client.
  1. Open Claude Desktop and navigate to Settings -> Developer -> Edit Config. This opens the configuration file that controls which MCP servers Claude can access.
  2. Replace the content with a configuration like this:


```

{
"mcpServers":{
"math":{
"command":"npx",
"args":["mcp-remote","http://my-mcp-server.my-account.workers.dev/sse"]
}
}
}

```

This tells Claude to communicate with your MCP server running at `http://localhost:8787/sse`.
  1. Save the file and restart Claude Desktop (command/ctrl + R). When Claude restarts, a browser window will open showing your OAuth login page. Complete the authorization flow to grant Claude access to your MCP server.


Once authenticated, you'll be able to see your tools by clicking the tools icon in the bottom right corner of Claude's interface.
## Connect your remote MCP server to Cursor
[](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/#connect-your-remote-mcp-server-to-cursor)
To connect [Cursor ↗](https://www.cursor.com/) with your remote MCP server, choose `Type`: "Command" and in the `Command` field, combine the command and args fields into one (e.g.`npx mcp-remote https://your-worker-name.your-account.workers.dev/sse`).
## Connect your remote MCP server to Windsurf
[](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/#connect-your-remote-mcp-server-to-windsurf)
You can connect your remote MCP server to [Windsurf ↗](https://codeium.com/windsurf) by editing the [`mcp_config.json` file ↗](https://docs.codeium.com/windsurf/mcp), and adding the following configuration:
```

{
"mcpServers":{
"math":{
"command":"npx",
"args":["mcp-remote","http://my-mcp-server.my-account.workers.dev/sse"]
}
}
}

```

## Was this helpful?
[ Edit page](https://github.com/cloudflare/cloudflare-docs/edit/production/src/content/docs/agents/guides/test-remote-mcp-server.mdx)
Last updated: Mar 20, 2025
[ Previous Build a remote MCP server ](https://developers.cloudflare.com/agents/guides/remote-mcp-server/) [ Next Model Context Protocol (MCP) ](https://developers.cloudflare.com/agents/model-context-protocol/)
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