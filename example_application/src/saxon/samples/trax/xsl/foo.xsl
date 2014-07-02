<xsl:stylesheet 
      xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'
      xmlns:bar="http://apache.org/bar"
      exclude-result-prefixes="bar"
      >
      
  <xsl:include href="inc1/inc1.xsl"/>
      
  <xsl:param name="a-param">default param value</xsl:param>

  <xsl:output encoding="iso-8859-1"/>
  
  <xsl:template match="/">
    <xsl:comment><xsl:value-of select="system-property('xsl:product-version')"/></xsl:comment>
    <xsl:next-match/>
  </xsl:template>  
  
  <xsl:template match="bar:element">
    <bar>
      <param-val>
        <xsl:value-of select="$a-param"/><xsl:text>, </xsl:text>
        <xsl:value-of select="$my-var"/>
      </param-val>
      <data><xsl:apply-templates/></data>
    </bar>
  </xsl:template>
      
  <xsl:template 
      match="@*|*|text()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates 
         select="@*|*|text()|processing-instruction()"/>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>