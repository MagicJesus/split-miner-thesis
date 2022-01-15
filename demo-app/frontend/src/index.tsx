import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App";
import axios from "axios";

axios.defaults.baseURL = process.env.REACT_APP_API_BASEURL;

ReactDOM.render(<App />, document.getElementById("root"));
