<!-- This stylesheet demonstrates the use of element extensibility with SAXON -->
<!-- Requires Saxon-PE or Saxon-EE -->

<xsl:stylesheet
	xmlns:sql="http://saxon.sf.net/sql"
 	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:saxon="http://saxon.sf.net/"
	xmlns:java="http://saxon.sf.net/java-type"
 	extension-element-prefixes="saxon"
 	exclude-result-prefixes="java">

<!-- insert your database details here, or supply them in parameters -->
<xsl:param name="driver" select="'sun.jdbc.odbc.JdbcOdbcDriver'"/>
<xsl:param name="database" select="'jdbc:odbc:test'"/>  
<xsl:param name="user"/>
<xsl:param name="password"/>

<!-- This stylesheet writes the book list to a SQL database -->

<xsl:variable name="count" select="0" saxon:assignable="yes"/>

<xsl:output method="xml" indent="yes"/>

<xsl:template match="BOOKLIST">
    <xsl:if test="not(element-available('sql:connect'))">
        <xsl:message>sql:connect is not available</xsl:message>
    </xsl:if>
    <xsl:message>Connecting to <xsl:value-of select="$database"/>...</xsl:message>
    <xsl:variable name="connection" as="java:java.sql.Connection?">
        <!-- the 'as' allows an empty sequence, because that's what's produced in the fallback case -->
        <sql:connect database="{$database}" user="{$user}" password="{$password}"
		    driver="{$driver}" xsl:extension-element-prefixes="sql">
	        <xsl:fallback>
	            <xsl:message terminate="yes">SQL extensions are not installed</xsl:message>
            </xsl:fallback>
        </sql:connect>
    </xsl:variable>
    <xsl:message>Connected...</xsl:message>
    <xsl:apply-templates select="BOOKS">
       <xsl:with-param name="connection" select="$connection"/>
    </xsl:apply-templates>
    <xsl:message>Inserted <xsl:value-of select="$count"/> records.</xsl:message>

    <xsl:variable name="book-table">
    <sql:query connection="$connection" table="book" column="*" row-tag="book" column-tag="col"
               xsl:extension-element-prefixes="sql"/> 
    </xsl:variable>
    
    <xsl:message>There are now <xsl:value-of select="count($book-table//book)"/> books.</xsl:message>
    <new-book-table>
        <xsl:copy-of select="$book-table"/>
    </new-book-table>
    
    <sql:close connection="$connection" xsl:extension-element-prefixes="sql">
       <xsl:fallback/>
    </sql:close>
</xsl:template>

<xsl:template match="BOOKS">
   <xsl:param name="connection"/>
    <xsl:for-each select="ITEM">
    	<sql:insert table="book" connection="$connection" xsl:extension-element-prefixes="sql">
	    <sql:column name="title" select="TITLE"/>
            <sql:column name="author" select="AUTHOR"/>
            <sql:column name="category" select="@CAT"/>
    	</sql:insert>
	<saxon:assign name="count" select="$count+1"/>
    </xsl:for-each>
</xsl:template>

</xsl:stylesheet>	
