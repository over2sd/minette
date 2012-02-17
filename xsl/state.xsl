<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="record.css" />
		<title>TCS: State of <xsl:value-of select="state/name"/></title>
	</head>
<body>
<a href="main.htm">Return to Main</a>
<h1><xsl:value-of select="state/name" /></h1>
<div class="nam">Start:</div><div class="con"> <xsl:value-of select="state/start"/> (<xsl:value-of select="state/scue"/>)</div>
<div class="nam">End:</div><div class="con"> <xsl:value-of select="state/end"/> (<xsl:value-of select="state/ecue"/>)</div>
<h1>Cities</h1>
<xsl:for-each select="state/city">
<xsl:sort select="name" /><div class="qcon"><a href="{file}" class="city"><xsl:value-of select="name"/></a></div>
</xsl:for-each>
<div class="spacer"> </div>
<div>XSL Template updated 09/06/3b</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>