import {
  GridItem,
  Heading,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
} from "@chakra-ui/react";
import React from "react";
import { NumberInputParameterProps } from "../../const/types";

const NumberInputParameter = ({
  register,
  name,
}: NumberInputParameterProps) => {
  return (
    <GridItem colSpan={1} rowSpan={2}>
      <Heading as="h5" size="xsm">
        {name}:
      </Heading>
      <NumberInput step={0.1} min={0} max={1} defaultValue={0.1}>
        <NumberInputField {...register(name)} />
        <NumberInputStepper>
          <NumberIncrementStepper />
          <NumberDecrementStepper />
        </NumberInputStepper>
      </NumberInput>
    </GridItem>
  );
};

export default NumberInputParameter;
