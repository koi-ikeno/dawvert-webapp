import { h } from "preact";
import Helmet from "preact-helmet";

const About = ({ title }) => {
  return (
    <main>
      <Helmet title={title} />

      <section>
        <h2>How it works?</h2>

        <p>
          SavingMIDIfromCaustic extracts midi sequence data from a .caustic file using 
          {" "}
          <a href="https://github.com/mozilla/mozjpeg">DawVert</a>, and brings it inside
          the browser thanks to{" "}
          <a href="https://webassembly.org/">Pyodide</a>.
        </p>
        <h2>Credit</h2>
        <p>
          The web UI is created by modifying his source code repository(MIT).
          {" "}
          <a href="https://github.com/mozilla/mozjpeg">DawVert</a>, and brings it inside
          {" "}
          <a href="https://webassembly.org/">Pyodide</a>.
        </p>
      </section>
    </main>
  );
};

export default About;
