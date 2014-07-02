<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">

<!-- parameter "dir" must be set from the command line: it represents the output directory -->

<xsl:variable name="backcolor" select="'#FFFFCC'" />
<xsl:variable name="panelcolor" select="'#88FF88'" />

<xsl:param name="dir" required="yes" as="xs:string"/>

<xsl:output name="play" method="html"/>
<xsl:output name="scene" method="html"/>

<xsl:template match="PLAY">
    <xsl:if test="not($dir)">
        <xsl:message terminate="yes">Parameter "dir" has not been set</xsl:message>
    </xsl:if>
    <xsl:result-document href="{$dir}/play.html" format="play">
    <html>
      <head>
        <title><xsl:apply-templates select="TITLE"/></title>
      </head>
      <body bgcolor='{$backcolor}'>
        <center>
            <h1><xsl:value-of select="TITLE"/></h1>
            <h3><xsl:apply-templates select="PLAYSUBT"/></h3>
            <i><xsl:apply-templates select="SCNDESCR"/></i>
        </center>
        <br/><br/>
        <table>
          <tr>
            <td width='350' valign='top' bgcolor='{$panelcolor}'>
              <xsl:apply-templates select="PERSONAE"/>
            </td>
            <td width='30'></td>
            <td valign='top'>
              <xsl:apply-templates select="PROLOGUE | ACT | EPILOGUE"/>
            </td>
          </tr>
        </table>
        <hr/>
      </body>
    </html>
    </xsl:result-document>
</xsl:template>

<xsl:template match="ACT/TITLE">
    <center>
      <h3>
	    <xsl:apply-templates/>
      </h3>
    </center>
</xsl:template>

<xsl:template match="PLAYSUBT">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="PERSONAE">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="PERSONAE/TITLE">
    <center>
      <h3>
	    <xsl:apply-templates/>
      </h3>
    </center>
</xsl:template>

<xsl:template match="PERSONAE/PERSONA">
    <table>
      <tr>
        <td valign="top">
	      <xsl:apply-templates/>
        </td>
      </tr>
    </table>
</xsl:template>

<xsl:template match="PGROUP">
    <table>
      <tr>
        <td width="160" valign="top">
	      <xsl:apply-templates select="PERSONA"/>
	    </td>
	    <td width="20"></td>
	    <td valign="bottom">
	      <i>
	        <xsl:apply-templates select="GRPDESCR"/>
	      </i>
	    </td>
	  </tr>
	</table>
</xsl:template>

<xsl:template match="PGROUP/PERSONA">
    <xsl:apply-templates/>
    <br/>
</xsl:template>

<xsl:template match="PGROUP/GRPDESCR">
    <xsl:apply-templates/>
    <br/>
</xsl:template>

<xsl:template match="SCNDESCR">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="ACT">
    <hr/>
	<xsl:apply-templates/>
    <xsl:if test="position()=last()"><hr/></xsl:if>
</xsl:template>

<xsl:template match="SCENE|PROLOGUE|EPILOGUE">
    <xsl:variable name="NR"><xsl:number count="SCENE|PROLOGUE|EPILOGUE" level="any"/></xsl:variable>
    <xsl:variable name="play"><xsl:value-of select="ancestor::PLAY/TITLE"/></xsl:variable>
    <xsl:variable name="act"><xsl:value-of select="ancestor::ACT/TITLE"/></xsl:variable>

    <a href="scene{$NR}.html">
        <xsl:value-of select="TITLE" />
    </a>
    <br/>

    <xsl:result-document href="{$dir}/scene{$NR}.html" format="scene">
      <html>
        <head>
          <title>
            <xsl:value-of select="concat($play, ' ', $act, ': ', TITLE)"/>
          </title>
        </head>
        <body bgcolor='{$backcolor}'>
          <p>
            <a href="play.html"><xsl:value-of select="$play"/></a>
            <br/>
            <b><xsl:value-of select="$act"/></b>
            <br/>
          </p>
          <xsl:apply-templates/>
        </body>
      </html>
    </xsl:result-document>
</xsl:template>

<xsl:template match="SCENE/TITLE | PROLOGUE/TITLE | EPILOGUE/TITLE">
    <h1>
      <center>
	    <xsl:apply-templates/>
	  </center>
	</h1>
	<hr/>
</xsl:template>

<xsl:template match="SPEECH">
    <table>
      <tr>
        <td width="160" valign="top">
	      <xsl:apply-templates select="SPEAKER"/>
        </td>
        <td table="top">
          <xsl:apply-templates select="STAGEDIR|LINE"/>
        </td>
	  </tr>
	</table>
</xsl:template>

<xsl:template match="SPEAKER">
    <b>
      <xsl:apply-templates/>
      <xsl:if test="not(position()=last())"><br/></xsl:if>
    </b>
</xsl:template>

<xsl:template match="SCENE/STAGEDIR">
    <center>
      <h3>
	    <xsl:apply-templates/>
	  </h3>
	</center>
</xsl:template>

<xsl:template match="SPEECH/STAGEDIR">
    <p>
      <i>
	    <xsl:apply-templates/>
	  </i>
	</p>
</xsl:template>

<xsl:template match="LINE/STAGEDIR">
    <xsl:text> [ </xsl:text>
    <i>
	  <xsl:apply-templates/>
	</i>
	<xsl:text> ] </xsl:text>
</xsl:template>

<xsl:template match="SCENE/SUBHEAD">
    <center>
      <h3>
	    <xsl:apply-templates/>
	  </h3>
	</center>
</xsl:template>

<xsl:template match="SPEECH/SUBHEAD">
    <p>
      <b>
	    <xsl:apply-templates/>
	  </b>
	</p>
</xsl:template>

<xsl:template match="LINE">
	<xsl:apply-templates/>
	<br/>
</xsl:template>

</xsl:stylesheet>	
