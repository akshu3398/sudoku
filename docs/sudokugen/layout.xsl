<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="weblog"
        xsl:version="1.0">

<xsl:import href="../../layout.xsl"/>

<xsl:param name="special"/>

<xsl:template name="content-body">
        <div class="content"><div class="contentbody">
        <xsl:choose>
            <xsl:when test="$special">
                <xsl:copy-of select="html/body/div[@id='specialcontent']/*"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="html/body/div[@id='content']/*"/>
            </xsl:otherwise>
        </xsl:choose>
        </div>
        </div>
</xsl:template>

<!--
<xsl:template name="content-ads">
        <div id="adsense">
        <xsl:copy-of select="html/body/div[@id='adsense']/*"/>
        </div>
</xsl:template>
-->


</xsl:stylesheet>
