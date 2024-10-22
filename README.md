# SMS Work Assistant Chatbot
## Project Setup

To set up the project, follow these steps:

<ol>
    <li>Run <code>docker compose build</code></li>
    <li>Then <code>docker compose up</code></li>
</ol>

<p>The project is accessible on port <code>9000</code> and on the endpoint <code>/recieve/sms</code></p>

<h2>Endpoint Structure</h2>
<p>The current structure that the endpoint receives is as follows:</p>

<ul>
    <li><code>Body</code> should contain the message</li>
    <li><code>From</code> should contain the number or unique key of the message source</li>
</ul>

<h3>Sample Request</h3>
<pre>
<code>
var formdata = new FormData();
formdata.append("Body", "Hi, A sample message");
formdata.append("From", "0300");
</code>
</pre>

<p>Make sure to create a <code>.env</code> file in the root folder and place the content in it like <code>env.sample</code>.</p>

<p><strong>To Furthur understand the project you can open the documentation.html file present in this repository.</strong></p>
