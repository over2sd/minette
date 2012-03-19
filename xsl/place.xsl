<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="record.css" />
		<title>TCS: <xsl:value-of select="place/commonname"/></title>
	</head>
<body>
<a href="main.htm">Return to Main</a>
<h1>Place</h1>
<div class="nam">Name:</div><div class="con"> <xsl:value-of select="place/name"/></div>
<div class="nam">Start:</div><div class="con"> <xsl:value-of select="place/start"/> (<xsl:value-of select="place/scue"/>)</div>
<div class="nam">End:</div><div class="con"> <xsl:value-of select="place/end"/> (<xsl:value-of select="place/ecue"/>)</div>
<h1>Stories</h1>
<div class="nam">Stories:</div><div class="con"> <xsl:value-of select="place/stories"/></div>
<div class="nam">First Mentions:</div><div class="con"> <xsl:value-of select="place/mention"/></div>
<h1>Specifications</h1>
<div class="nam">Description:</div><div class="con"> <xsl:value-of select="place/desc"/></div>
<div class="nam">Address:</div><div class="con"> <xsl:value-of select="place/address"/></div>
<div class="nam">Location:</div><div class="con"> <a href="{place/locfile}.xml"><xsl:value-of select="place/loc"/></a>, <a href="{place/statefile}.xml"><xsl:value-of select="place/state"/></a></div>
<div class="nam">Notes:</div><div class="con"> <xsl:for-each select="place/note"><div><xsl:value-of select="content" /> (<xsl:value-of select="date" />)</div></xsl:for-each></div>
<h1>Characters</h1>
<h2>Legitimate Connection</h2>
<xsl:for-each select="place/relat[rtype='fam']">
<xsl:sort select="realm"/>
<div class="relat"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each></div>
<xsl:for-each select="realm"><div class="realm"><xsl:value-of select="realm"/></div></xsl:for-each>
</xsl:for-each>
<xsl:for-each select="place/relat[rtype='empl']">
<xsl:sort select="realm"/>
<div class="relat"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each></div>
<xsl:for-each select="realm"><div class="realm"><xsl:value-of select="realm"/></div></xsl:for-each>
</xsl:for-each>
<h2>Others</h2>
<xsl:for-each select="place/relat[rtype='other']">
<xsl:sort select="realm"/>
<div class="relat nam"><xsl:value-of select="relation"/>
</div><div class="con"> <a href="{file}.xml" class="{cat}"><xsl:value-of select="related"/></a> 
<xsl:for-each select="events/mstone"><span class="event"><xsl:value-of select="event"/>: <xsl:value-of select="date"/></span></xsl:for-each></div>
<xsl:for-each select="realm"><div class="realm"><xsl:value-of select="/place/relat/realm"/></div></xsl:for-each>
</xsl:for-each>
<div class="spacer"> </div>
<div>XML Document updated <xsl:value-of select="/place/update"/></div>
<div>XSL Template updated 09/06/3b</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
