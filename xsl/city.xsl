<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="record.css" />
		<title>TCS: City of <xsl:value-of select="city/name"/></title>
	</head>
<body>
<a href="main.htm">Return to Main</a>
<h1><xsl:value-of select="city/name" />, <a href="{city/statefile}"><xsl:value-of select="city/state"/></a></h1>
<div class="nam">Start:</div><div class="con"> <xsl:value-of select="city/start"/> (<xsl:value-of select="city/scue"/>)</div>
<div class="nam">End:</div><div class="con"> <xsl:value-of select="city/end"/> (<xsl:value-of select="city/ecue"/>)</div>
<h1>Places</h1>
<ol class="ncon"><xsl:for-each select="city/place">
<xsl:sort select="name" /><li><a href="{file}" class="place"><xsl:value-of select="name"/></a>
<xsl:value-of select="note" />
</li>
</xsl:for-each></ol>
<div class="spacer"> </div>
<div>XSL Template updated 09/06/3b</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>