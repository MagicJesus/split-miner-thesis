import { HandleSubmitArguments } from "../const/types";
import axios from "axios";

export const handleParametersSubmit = ({
  data,
  file,
}: HandleSubmitArguments): Promise<void> => {
  const headers = {
    "Content-Type": "multipart/form-data",
  };

  const formData = new FormData();
  formData.append("file", file, file.name);
  formData.append(
    "concurrency-threshold",
    String(data["Concurrency threshold"])
  );
  formData.append("filtering-percentile", String(data["Filtering percentile"]));
  formData.append("artificial-log", String(data["Artificial log"]));

  return axios.post("upload", formData, { headers });
};
