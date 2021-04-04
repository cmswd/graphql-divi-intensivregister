import React from "react";
import { render } from "react-dom";
import DataGrid from 'react-data-grid';
import {
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  useQuery,
  gql
} from "@apollo/client";

const client = new ApolloClient({
  uri: "http://localhost:8080/v1/graphql",
  cache: new InMemoryCache()
});

function Test () {
  const { loading, error, data } = useQuery(gql`
  {
    datasets(where: {county_code: {_eq: "02000"}}, order_by: {daten_stand: asc}) {
      daten_stand
      betten_frei
      betten_belegt
    }
  }
`);

if (loading) return <p>Loading...</p>;
if (error) return <p>Error :(</p>;

  const columns = [
    { key: 'date', name: 'date'},
    { key: 'free', name: 'free capacity' },
    { key: 'occupied', name: 'occupied capacity' }
  ];

  const rows = data.datasets.map(({ daten_stand, betten_frei, betten_belegt }) => ({date: daten_stand, free: betten_frei, occupied: betten_belegt}))
    
  return (<DataGrid
    columns={columns}
    rows={rows}
    />);

}

function States() {
  const { loading, error, data } = useQuery(gql`
    {
      states {
        name
      }
    }
  `);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  const columns = [
    { key: 'name', name: 'name of the state' }
  ];

  const rows = data.states.map(({ name }) => ({name}))
    
  return (<DataGrid
    columns={columns}
    rows={rows}
    />);
}

function Counties() {
  const { loading, error, data } = useQuery(gql`
    {
      counties {
        name
        state {
          name
        }
      }
    }
  `);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  const columns = [
    { key: 'name', name: 'name of the county' },
    { key: 'state', name: 'name of the state'}
  ];

  const rows = data.counties.map(({ name, state }) => ({name: name, state: state.name}))
    
  return (<DataGrid
    columns={columns}
    rows={rows}
    />);
}

function App() {
  return (
    <ApolloProvider client={client}>
      <div>
        <h2>🚀 List of states 🚀</h2>
        <States />
      </div>
      <div>
        <h2>🚀 List of counties 🚀</h2>
        <Counties />
      </div>
      <div>
        <h2>🚀 Capacity in Hamburg 🚀</h2>
        <Test />
      </div>
    </ApolloProvider>
  );
}

render(<App />, document.getElementById("root"));
