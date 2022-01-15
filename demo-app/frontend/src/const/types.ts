import { UnpackNestedValue, UseFormRegister } from "react-hook-form";

export enum ParameterName {
  concurrencyThreshold = "Concurrency threshold",
  filteringPercentile = "Filtering percentile",
  artificialLog = "Artificial log",
}

export interface FormValues {
  [ParameterName.concurrencyThreshold]: number;
  [ParameterName.filteringPercentile]: number;
  [ParameterName.artificialLog]: boolean;
}

export interface ModelParametersProps {
  register: UseFormRegister<FormValues>;
}

export interface HandleSubmitArguments {
  data: UnpackNestedValue<FormValues>;
  file: File;
}

export interface NumberInputParameterProps extends ModelParametersProps {
  name: ParameterName;
}
