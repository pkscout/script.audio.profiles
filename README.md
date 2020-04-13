<h1>script.audio.profiles</h1>
<h2>Easy switch between different audio settings.</h2>

Save audio settings to profiles and easy switch between them using keymap or pop-up menu:

<pre>RunScript(script.audio.profiles,0) - one keymap to toggle switch between two profiles. </pre>
<pre>RunScript(script.audio.profiles,x) - where x is number of profile</pre>
<pre>RunScript(script.audio.profiles,popup) - display popup to change profile </pre>

<h2>Information</h2>
The plug originally came from here: https://github.com/Regss/script.audio.profiles and here: https://github.com/CtrlGy/script.audio.profiles
<br/>A friend corrected the code for me, I throw it to share with others.

<h2>Download:</h2>
The repository is currently being tested. Download using "Download" and install using a zip file. 
</br>
<b>I plan to create a separate repository only for this add-on. </b>
<h2>Short Instruction:</h2>
<ol>
  <li>Configure Add-on to set names for profiles.</li>
  <li>To save current audio settings to profile run Add-on from programs section.</li>
</ol>

<h2>Configuration Instruction:</h2>

<h3>Step 1</h3>
Go to Programs -> Audio profile -> not run it but choose from context menu -> Configure Add-on
Enable two profiles and add it names that you want

<h3>Step 2</h3>
Go to System -> Audio settings</br>
Set settings for first profile for example TV by the analog output 2.0</br>
Go to Programs -> Audio profile -> run it</br>
Save settings as first profile</br>

<h3>Step 3</h3>
Repeat Step 2 and set settings for digital like SPDIF or HDMI and save as second profile

<h3>Step 4</h3>
No you can switch between profiles using key map. I suggest to test it on keyboard keymap.
Edit or create file keyboard.xml in userdata/keymaps/ and past this code:
</br>
<b>Example 1</b> - keymap for each profile.
<pre>
&lt;keymap>
  &lt;global>
    &lt;keyboard>
      &lt;t>RunScript(script.audio.profiles,1)&lt;/t>
      &lt;a>RunScript(script.audio.profiles,2)&lt;/a>
    &lt;/keyboard>
  &lt;/global>
&lt;/keymap>
</pre>

<b>Example 2</b> - keymap for toggle between profiles.
<pre>
&lt;keymap>
  &lt;global>
    &lt;keyboard>
      &lt;t>RunScript(script.audio.profiles,0)&lt;/t>
    &lt;/keyboard>
  &lt;/global>
&lt;/keymap>
</pre>

<b>Example 3</b> - keymap for Window Popup.</br>
<pre>
&lt;keymap>
  &lt;global>
    &lt;keyboard>
      &lt;t>RunScript(script.audio.profiles,popup)&lt;/t>
    &lt;/keyboard>
  &lt;/global>
&lt;/keymap>
</pre>

<b>Example 4</b> - Window Popup when start playing.</br>
In addon settings enable option "Show audio stream select menu on start playing". This will show popup to choose audio profile every time when you start play.

<b>Example 5</b> - Automatic switch for different content.</br>
In Addon settings go to category "Automatic switch" then select for which types of content which profile will be automatically switched on.


