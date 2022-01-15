import { Checkbox, GridItem } from "@chakra-ui/react";
import React from "react";
import { ModelParametersProps, ParameterName } from "../../const/types";
import NumberInputParameter from "./NumberInputParameter";

const ModelParameters = ({ register }: ModelParametersProps) => {
  return (
    <>
      <NumberInputParameter
        register={register}
        name={ParameterName.concurrencyThreshold}
      />
      <NumberInputParameter
        register={register}
        name={ParameterName.filteringPercentile}
      />
      <GridItem colSpan={1}>
        <Checkbox
          {...register(ParameterName.artificialLog)}
          colorScheme="green"
          defaultIsChecked={false}
        >
          {ParameterName.artificialLog}
        </Checkbox>
      </GridItem>
    </>
  );
};

export default ModelParameters;
