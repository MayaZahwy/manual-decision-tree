import type { BurnoutFormValues, WeekendsValue } from "../types/tree";

interface BurnoutFormProps {
  values: BurnoutFormValues;
  onChange: (values: BurnoutFormValues) => void;
  onSubmit: () => void;
  loading: boolean;
  disabled: boolean;
}

export default function BurnoutForm({
  values,
  onChange,
  onSubmit,
  loading,
  disabled,
}: BurnoutFormProps) {
  const update = (patch: Partial<BurnoutFormValues>) => {
    onChange({ ...values, ...patch });
  };

  return (
    <form
      className="burnout-form"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="form-field">
        <label htmlFor="sleep">
          Sleep (hours): <strong>{values.sleep.toFixed(1)}</strong>
        </label>
        <input
          id="sleep"
          type="range"
          min={3}
          max={10}
          step={0.5}
          value={values.sleep}
          onChange={(event) => update({ sleep: Number(event.target.value) })}
        />
        <input
          type="number"
          min={0}
          max={24}
          step={0.5}
          value={values.sleep}
          onChange={(event) => update({ sleep: Number(event.target.value) })}
          aria-label="Sleep hours number input"
        />
      </div>

      <div className="form-field">
        <label htmlFor="meetings">
          Meetings per day: <strong>{values.meetings}</strong>
        </label>
        <input
          id="meetings"
          type="range"
          min={0}
          max={12}
          step={1}
          value={values.meetings}
          onChange={(event) => update({ meetings: Number(event.target.value) })}
        />
        <input
          type="number"
          min={0}
          max={20}
          step={1}
          value={values.meetings}
          onChange={(event) => update({ meetings: Number(event.target.value) })}
          aria-label="Meetings number input"
        />
      </div>

      <fieldset className="form-field weekends-field">
        <legend>Works on weekends?</legend>
        <label>
          <input
            type="radio"
            name="weekends"
            value="NO"
            checked={values.weekends === "NO"}
            onChange={() => update({ weekends: "NO" as WeekendsValue })}
          />
          No
        </label>
        <label>
          <input
            type="radio"
            name="weekends"
            value="YES"
            checked={values.weekends === "YES"}
            onChange={() => update({ weekends: "YES" as WeekendsValue })}
          />
          Yes
        </label>
      </fieldset>

      <div className="form-field">
        <label htmlFor="stress">
          Stress level (1-10): <strong>{values.stress}</strong>
        </label>
        <input
          id="stress"
          type="range"
          min={1}
          max={10}
          step={1}
          value={values.stress}
          onChange={(event) => update({ stress: Number(event.target.value) })}
        />
      </div>

      <button type="submit" className="primary-button" disabled={disabled || loading}>
        {loading ? "Predicting..." : "Predict Burnout Level"}
      </button>
    </form>
  );
}
