<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="record.css" />
		<title>TCS: <xsl:value-of select="person/commonname"/></title>
	</head>
<body>
<a href="index.htm">Return to world index</a>
<h1>Person</h1>
<div class="nam">Title:</div><div class="con"> <xsl:value-of select="person/ctitle"/></div>
<div class="nam">Name:</div><div class="con"><xsl:choose><xsl:when test="person/nameorder='fg'">
<xsl:value-of select="person/fname"/> <xsl:value-of select="person/gname"/> <xsl:value-of select="person/mname"/></xsl:when><xsl:otherwise>
<xsl:value-of select="person/gname"/> <xsl:value-of select="person/mname"/> <xsl:value-of select="person/fname"/></xsl:otherwise></xsl:choose></div>
<div class="nam">Nickname:</div><div class="con"> <xsl:value-of select="person/nname"/></div>
<div class="nam">Gender:</div><div class="con"> <xsl:value-of select="person/gender"/></div>
<div class="nam">Birth:</div><div class="con"> <xsl:value-of select="person/bday"/></div>
<div class="nam">Death:</div><div class="con"> <xsl:value-of select="person/dday"/></div>
<h1>Stories</h1>
<div class="nam">Stories:</div><div class="con"> <xsl:value-of select="person/stories"/></div>
<div class="nam">First Mention:</div><div class="con"> <xsl:value-of select="person/mention"/></div>
<div class="nam">First Appearance (ch):</div><div class="con"> <xsl:value-of select="person/appear1ch"/></div>
<div class="nam">First Appearance (wr):</div><div class="con"> <xsl:value-of select="person/appear1wr"/></div>
<div class="nam">Conflict:</div><div class="con"> <xsl:value-of select="person/conflict"/></div>
<div class="nam">Relation to lead(s):</div><div class="con"> <xsl:value-of select="person/leadrel"/></div>
<h1>Physical Appearance</h1>
<div class="nam">Body Type:</div><div class="con"> <xsl:value-of select="person/bodytyp"/></div>
<div class="nam">Age:</div><div class="con"> <xsl:value-of select="person/age"/></div>
<div class="nam">Skin:</div><div class="con"> <xsl:value-of select="person/skin"/></div>
<div class="nam">Eyes:</div><div class="con"> <xsl:value-of select="person/eyes"/></div>
<div class="nam">Hair:</div><div class="con"> <xsl:value-of select="person/hair"/></div>
<div class="nam">Distinguishing Marks:</div><div class="con"> <xsl:value-of select="person/dmarks"/></div>
<div class="nam">Dress:</div><div class="con"> <xsl:value-of select="person/dress"/></div>
<div class="nam">Attached Possessions:</div><div class="con"> <xsl:value-of select="person/attposs"/></div>
<div class="nam">Associated Smell:</div><div class="con"> <xsl:value-of select="person/asmell"/></div>
<h1>Personality Traits</h1>
<div class="nam">Personality:</div><div class="con"> <xsl:value-of select="person/personality"/></div>
<div class="nam">Distinct Speech:</div><div class="con"> <xsl:value-of select="person/speech"/></div>
<div class="nam">Former Occupation:</div><div class="con"> <xsl:value-of select="person/formocc/pos"/><xsl:for-each select="person/formocc/events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each></div>
<div class="nam">Current Occupation:</div><div class="con"> <xsl:value-of select="person/currocc/pos"/><xsl:for-each select="person/currocc/events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each></div>
<div class="nam">Strength:</div><div class="con"> <xsl:value-of select="person/strength"/></div>
<div class="nam">Weakness:</div><div class="con"> <xsl:value-of select="person/weak"/></div>
<div class="nam">Mole:</div><div class="con"> <xsl:value-of select="person/mole"/></div>
<div class="nam">Hobbies:</div><div class="con"> <xsl:value-of select="person/hobby"/></div>
<h1>Miscellany</h1>
<div class="nam">Misc:</div><div class="con"> <xsl:value-of select="person/misc"/></div>
<div class="nam">Ethnic background:</div><div class="con"> <xsl:value-of select="person/ethnic"/></div>
<div class="nam">Origin:</div><div class="con"> <xsl:value-of select="person/origin"/></div>
<div class="nam">Background:</div><div class="con"> <xsl:value-of select="person/backstory"/></div>
<div class="nam">Place of Residence:</div><div class="con"> <xsl:value-of select="person/residence"/></div>
<div class="nam">Minor Related Chars:</div><div class="con"> <xsl:value-of select="person/minchar"/></div>
<div class="nam">Talents:</div><div class="con"> <xsl:value-of select="person/talent"/></div>
<div class="nam">Abilities:</div><div class="con"> <xsl:value-of select="person/abil"/></div>
<div class="nam">Story Goal:</div><div class="con"> <xsl:value-of select="person/sgoal"/></div>
<div class="nam">Other Notes:</div><div class="con"> <xsl:value-of select="person/other"/></div>
<h1>Relationships</h1>
<h2>Family</h2>
<xsl:for-each select="person/relat[rtype='fam']">
<xsl:sort select="realm"/>
<div class="relat"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each><xsl:for-each select="realm"><div class="realm"><xsl:value-of select="../realm"/></div></xsl:for-each></div>
</xsl:for-each>
<h2>Friends</h2>
<xsl:for-each select="person/relat[rtype='friend']">
<xsl:sort select="realm"/>
<div class="relat"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each><xsl:for-each select="realm"><div class="realm"><xsl:value-of select="../realm"/></div></xsl:for-each></div>
</xsl:for-each>
<h2>Work</h2>
<xsl:for-each select="person/relat[rtype='work']">
<xsl:sort select="realm"/>
<div class="relat"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each><xsl:for-each select="realm"><div class="realm"><xsl:value-of select="../realm"/></div></xsl:for-each></div>
</xsl:for-each>
<h1>Places</h1>
<xsl:for-each select="person/relat[rtype='place']">
<xsl:sort select="realm"/>
<div class="relat"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each><xsl:for-each select="realm"><div class="realm"><xsl:value-of select="../realm"/></div></xsl:for-each></div>
</xsl:for-each>
<div class="spacer"> </div>
<div>XML Document updated <xsl:value-of select="/person/update"/></div>
<div>XSL Template updated 09/06/3b</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
