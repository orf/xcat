<xsl:transform
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:xs="http://www.w3.org/2001/XMLSchema"
 xmlns:f="http://localhost/functions"
 exclude-result-prefixes="xs f"
 version="2.0"
>

<!-- This stylesheet summarizes the contents of the input XML file, displaying
     the names of the elements encountered and the number of occurrences of each -->

<xsl:output method="xml" indent="yes"/>

<xsl:param name="include-attributes" as="xs:boolean" select="false()"/>

<xsl:template match="/">
  <summary of="{document-uri(.)}">
    <xsl:for-each-group select="//* | //@*[$include-attributes]" group-by="f:path(.)">
      <xsl:sort select="current-grouping-key()"/>
      <element path="{current-grouping-key()}" count="{count(current-group())}"/>
    </xsl:for-each-group>
  </summary>
</xsl:template>

<xsl:function name="f:path" as="xs:string">
  <xsl:param name="node" as="node()"/>
  <xsl:sequence select="$node/(
    if (. instance of attribute())
    then concat(f:path(..), '/@', name())
    else string-join(ancestor-or-self::*/name(), '/'))"/>
</xsl:function>


</xsl:transform>	
