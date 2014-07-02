<xsl:stylesheet 
      xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'
      xmlns:date="java:java.util.Date"
      exclude-result-prefixes="date">

<!-- this stylesheet tests multi-document output by creating a new result document for each element -->

  <xsl:template match="/">
  <output>
    <xsl:attribute name="at" select="date:toString(date:new())" use-when="function-available('date:new', 0)"/>
    <xsl:apply-templates select="cities/*"/>
  </output>
  </xsl:template>  

  <xsl:template match="city">
    <xsl:result-document href="{@name}.out" encoding="iso-8859-1">
      <document>
         <xsl:copy-of select="@*"/>
         <xsl:apply-templates/>
      </document>
    </xsl:result-document>
  </xsl:template>
  
  <xsl:template match="town">
    <xsl:result-document href="{@name}.sax">
      <document>
         <xsl:copy-of select="@*"/>
         <xsl:apply-templates/>
      </document>
    </xsl:result-document>
  </xsl:template>  
      
</xsl:stylesheet>