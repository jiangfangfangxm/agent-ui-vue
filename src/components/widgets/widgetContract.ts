import type {
  UIComponent,
  UIComponentOfType,
  WidgetType,
  WorkflowEventInput,
} from "../../types/workflow";

export interface WidgetComponentLike {
  id: string;
  type: string;
}

export interface WidgetRuntimeState {
  allowedEvents: string[];
  isDispatching: boolean;
}

export type WidgetProps<T extends WidgetComponentLike = UIComponent> = {
  component: T;
  runtime: WidgetRuntimeState;
};

export type WidgetPropsOfType<T extends WidgetType> = WidgetProps<
  UIComponentOfType<T>
>;

export type WidgetDispatch = (event: WorkflowEventInput) => void;
