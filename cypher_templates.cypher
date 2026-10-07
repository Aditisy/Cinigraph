// Exercise 3: parameterized read-only templates
// In Neo4j Browser first set: :param entity => "The Matrix"
// and: :param limit => 10
// Change entity to a person name for filmographies.

// cast
MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) WHERE toLower(m.title)=toLower($entity) RETURN m.title AS movie, p.name AS actor, r.roles AS roles ORDER BY actor LIMIT $limit;

// director
MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE toLower(m.title)=toLower($entity) RETURN m.title AS movie, p.name AS director ORDER BY director LIMIT $limit;

// actor_movies
MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE toLower(p.name)=toLower($entity) RETURN m.title AS movie, m.released AS year ORDER BY year, movie LIMIT $limit;

// director_movies
MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE toLower(p.name)=toLower($entity) RETURN m.title AS movie, m.released AS year ORDER BY year, movie LIMIT $limit;

// movie
MATCH (m:Movie) WHERE toLower(m.title)=toLower($entity) RETURN m.title AS movie, m.released AS year, m.tagline AS tagline LIMIT $limit;

// recommend
MATCH (seed:Movie)<-[:ACTED_IN]-(p:Person)-[:ACTED_IN]->(m:Movie) WHERE toLower(seed.title)=toLower($entity) AND m<>seed WITH m, collect(DISTINCT p.name) AS shared_actors RETURN m.title AS movie, m.released AS year, shared_actors, size(shared_actors) AS score ORDER BY score DESC, movie LIMIT $limit;

