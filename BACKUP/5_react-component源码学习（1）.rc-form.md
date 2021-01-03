# [react-component源码学习（1） rc-form](https://github.com/sl1673495/blogs/issues/5)

rc-form作为ant-design系列实现表单组件的底层组件， 通用性和强大的功能兼得，这得益于它底层的精妙实现，rc-form是典型的高阶组件（higher-order component）

下面从一个官方的简单示例说起。 
```js
import { createForm, formShape } from 'rc-form';

class Form extends React.Component {
  static propTypes = {
    form: formShape,
  };

  submit = () => {
    this.props.form.validateFields((error, value) => {
      console.log(error, value);
    });
  }

  render() {
    let errors;
    const { getFieldProps, getFieldError } = this.props.form;
    return (
      <div>
        <input {...getFieldProps('normal')}/>
        <input {...getFieldProps('required', {
          onChange(){}, // have to write original onChange here if you need
          rules: [{required: true}],
        })}/>
        {(errors = getFieldError('required')) ? errors.join(',') : null}
        <button onClick={this.submit}>submit</button>
      </div>
    );
  }
}

export createForm()(Form);
```

可以看到在最后用createForm这个函数执行返回的函数包裹了Form组件，
正因为如此在render中才可以从props里拿到from， 这是rc-form提供给我们的，接下来看看这个form是如何注入进去的。

### createForm.js
```js
import createBaseForm from './createBaseForm';

export const mixin = {
  getForm() {
    return {
      getFieldsValue: this.fieldsStore.getFieldsValue,
      getFieldValue: this.fieldsStore.getFieldValue,
      getFieldInstance: this.getFieldInstance,
      setFieldsValue: this.setFieldsValue,
      setFields: this.setFields,
      setFieldsInitialValue: this.fieldsStore.setFieldsInitialValue,
      getFieldDecorator: this.getFieldDecorator,
      getFieldProps: this.getFieldProps,
      getFieldsError: this.fieldsStore.getFieldsError,
      getFieldError: this.fieldsStore.getFieldError,
      isFieldValidating: this.fieldsStore.isFieldValidating,
      isFieldsValidating: this.fieldsStore.isFieldsValidating,
      isFieldsTouched: this.fieldsStore.isFieldsTouched,
      isFieldTouched: this.fieldsStore.isFieldTouched,
      isSubmitting: this.isSubmitting,
      submit: this.submit,
      validateFields: this.validateFields,
      resetFields: this.resetFields,
    };
  },
};

function createForm(options) {
  return createBaseForm(options, [mixin]);
}

export default createForm;

```
这是我们在render中调用的createForm 可以看到mixin中的getForm里的属性和我们使用的很相似，其实这就是最终注入的props.form属性， 对外暴露的createForm方法最终调用了createBaseForm并将mixin传入。

### createBaseForm.js

```js
function createBaseForm(option = {}, mixins = []) {
  const {
    validateMessages,
    onFieldsChange,
    onValuesChange,
    mapProps = identity,
    mapPropsToFields,
    fieldNameProp,
    fieldMetaProp,
    fieldDataProp,
    formPropName = 'form',
    name: formName,
    // @deprecated
    withRef,
  } = option;

  return function decorate(WrappedComponent) {
    const Form = createReactClass({
      mixins,
      .......,
      render() {
        const { wrappedComponentRef, ...restProps } = this.props;
        const formProps = {
          [formPropName]: this.getForm(),
        };
        if (withRef) {
          if (process.env.NODE_ENV !== 'production' && process.env.NODE_ENV !== 'test') {
            warning(
              false,
              '`withRef` is deprecated, please use `wrappedComponentRef` instead. ' +
                'See: https://github.com/react-component/form#note-use-wrappedcomponentref-instead-of-withref-after-rc-form140'
            );
          }
          formProps.ref = 'wrappedComponent';
        } else if (wrappedComponentRef) {
          formProps.ref = wrappedComponentRef;
        }
        const props = mapProps.call(this, {
          ...formProps,
          ...restProps,
        });
        return <WrappedComponent {...props}/>;
      },
    });

    return argumentContainer(Form, WrappedComponent);
  };
}
```

可以看出createBaseForm是一个典型的高阶函数，接受options和mixin作为参数，返回一个装饰器decorate函数, 这个decorate函数接受一个react component作为参数，所以我们在外部调用可以使用
```js
createForm()(Form);
```
这样去获得一个注入了props的组件, 接下来看render中的实现
```js
        const formProps = {
          [formPropName]: this.getForm(),
        };
        return <WrappedComponent {...props}/>;
```
formPropName在defaultProps中默认被设置为'form', getForm是从mixin中注入的，
其实就相当于注入了
```js
{
  form: {
      getFieldsValue: this.fieldsStore.getFieldsValue,
      getFieldValue: this.fieldsStore.getFieldValue,
      getFieldInstance: this.getFieldInstance,
      setFieldsValue: this.setFieldsValue,
      setFields: this.setFields,
      setFieldsInitialValue: this.fieldsStore.setFieldsInitialValue,
      getFieldDecorator: this.getFieldDecorator,
      getFieldProps: this.getFieldProps,
      getFieldsError: this.fieldsStore.getFieldsError,
      getFieldError: this.fieldsStore.getFieldError,
      isFieldValidating: this.fieldsStore.isFieldValidating,
      isFieldsValidating: this.fieldsStore.isFieldsValidating,
      isFieldsTouched: this.fieldsStore.isFieldsTouched,
      isFieldTouched: this.fieldsStore.isFieldTouched,
      isSubmitting: this.isSubmitting,
      submit: this.submit,
      validateFields: this.validateFields,
      resetFields: this.resetFields,
  }
}
```

看源码先从主流程看起， 知道了form是如何注入以后，我们就从示例入手， 先看看
```js
<input {...getFieldProps('normal')}/>
```
中的getFieldProps是如何实现。

### getFieldProps
```js
getFieldProps(name, usersFieldOption = {}) {
        if (!name) {
          throw new Error('Must call `getFieldProps` with valid name string!');
        }
        if (process.env.NODE_ENV !== 'production') {
          warning(
            this.fieldsStore.isValidNestedFieldName(name),
            'One field name cannot be part of another, e.g. `a` and `a.b`.'
          );
          warning(
            !('exclusive' in usersFieldOption),
            '`option.exclusive` of `getFieldProps`|`getFieldDecorator` had been remove.'
          );
        }

        delete this.clearedFieldMetaCache[name];

        const fieldOption = {
          name,
          trigger: DEFAULT_TRIGGER,
          valuePropName: 'value',
          validate: [],
          ...usersFieldOption,
        };

        const {
          rules,
          trigger,
          validateTrigger = trigger,
          validate,
        } = fieldOption;

        const fieldMeta = this.fieldsStore.getFieldMeta(name);
        if ('initialValue' in fieldOption) {
          fieldMeta.initialValue = fieldOption.initialValue;
        }

        const inputProps = {
          ...this.fieldsStore.getFieldValuePropValue(fieldOption),
          ref: this.getCacheBind(name, `${name}__ref`, this.saveRef),
        };
        if (fieldNameProp) {
          inputProps[fieldNameProp] = formName ? `${formName}_${name}` : name;
        }

        const validateRules = normalizeValidateRules(validate, rules, validateTrigger);
        const validateTriggers = getValidateTriggers(validateRules);
        validateTriggers.forEach((action) => {
          if (inputProps[action]) return;
          inputProps[action] = this.getCacheBind(name, action, this.onCollectValidate);
        });

        // make sure that the value will be collect
        if (trigger && validateTriggers.indexOf(trigger) === -1) {
          inputProps[trigger] = this.getCacheBind(name, trigger, this.onCollect);
        }

        const meta = {
          ...fieldMeta,
          ...fieldOption,
          validate: validateRules,
        };
        this.fieldsStore.setFieldMeta(name, meta);
        if (fieldMetaProp) {
          inputProps[fieldMetaProp] = meta;
        }

        if (fieldDataProp) {
          inputProps[fieldDataProp] = this.fieldsStore.getField(name);
        }

        return inputProps;
      },
```
这个函数接受name，和usersFieldOption两个参数

```js
const fieldOption = {
          name,
          trigger: DEFAULT_TRIGGER, // onChange
          valuePropName: 'value',
          validate: [],
          ...usersFieldOption,
};

 const fieldMeta = this.fieldsStore.getFieldMeta(name);
 if ('initialValue' in fieldOption) {
    fieldMeta.initialValue = fieldOption.initialValue;
 }
```
先是一波简单的合并配置， 将usersFieldOption混入fiedOption中,
然后从this.fieldsStore中根据name提取出fieldMeta, 将initialValue填入。
fieldsStore是一个存储类，form组件内部有大量的数据需要存储和读取，所以实现了一个fieldsStore类去处理数据的流转。
```js
class FieldsStore {
  constructor(fields) {
    this.fields = this.flattenFields(fields);
    this.fieldsMeta = {};
  }
  ...
  getFieldMeta(name) {
    this.fieldsMeta[name] = this.fieldsMeta[name] || {};
    return this.fieldsMeta[name];
  }
}
```
因为初始化的this.fieldsStore应该是空的， 所以这里也只是读取到了一个空对象，继续往下走。
```js
const inputProps = {
   ...this.fieldsStore.getFieldValuePropValue(fieldOption),
   ref: this.getCacheBind(name, `${name}__ref`, this.saveRef),
};
```
inputProps中先是通过fieldsStore实例的getFieldValuePropValue方法传入fieldOption拿到一些属性，
在初始化的时候其实就是{ value: undefined }
```js
  getFieldValuePropValue(fieldMeta) {
    // 对应示例中 name: 'normal', valuePropName: 'value'
    const { name, getValueProps, valuePropName } = fieldMeta;
   // 得到 {  name: 'normal'  }， 初始化的时候fields还为空
    const field = this.getField(name);
   // field中没有value， 所以去取initialValue， 示例中未传入，同样为空 
    const fieldValue = 'value' in field ?
      field.value : fieldMeta.initialValue;
    if (getValueProps) {
      return getValueProps(fieldValue);
    }
   // 初始化的时候就返回 { value: undefined }
    return { [valuePropName]: fieldValue };
  }

  getField(name) {
    return {
      ...this.fields[name],
      name,
    };
  }
```

ref则是通过this.cacheBind的缓存方法去取缓存了的表单元素ref
此时inputProps = {
  value: undefined,
  ref: component,
}

接下来是处理有关表单验证的逻辑，
```js
const validateRules = normalizeValidateRules(validate, rules, validateTrigger);
const validateTriggers = getValidateTriggers(validateRules);
validateTriggers.forEach((action) => {
   if (inputProps[action]) return;
   inputProps[action] = this.getCacheBind(name, action, this.onCollectValidate);
});
```
normalizeValidateRules方法接受的validate在示例未传入，是空数组，rules是 [{required: true}], validateTrigger是默认的onChange, 看normalizeValidateRules的实现：
```js
export function normalizeValidateRules(validate, rules, validateTrigger) {
  const validateRules = validate.map((item) => {
    const newItem = {
      ...item,
      trigger: item.trigger || [],
    };
    if (typeof newItem.trigger === 'string') {
      newItem.trigger = [newItem.trigger];
    }
    return newItem;
  });
  if (rules) {
    validateRules.push({
      trigger: validateTrigger ? [].concat(validateTrigger) : [],
      rules,
    });
  }
  return validateRules;
}
```

我们发现其实返回了
```js
validateRules: [{
  trigger: ['onChange'],
  rules: [{required: true}]
}]
```

在看getValidateTriggers 将上面的数组传入
```js
export function getValidateTriggers(validateRules) {
  return validateRules
    .filter(item => !!item.rules && item.rules.length)
    .map(item => item.trigger)
    .reduce((pre, curr) => pre.concat(curr), []);
}
```
其实就是简单的把rules为空的项过滤掉, 因为每个rule的trigger可能有多个 所以reduce的目的是拉平成一维数组, 最后返回['onChange']这样的数组
```js
  validateTriggers = ['onChange']
```

最后对validateTriggers进行循环，循环体内
```js
if (inputProps[action]) return;
inputProps[action] = this.getCacheBind(name, action, this.onCollectValidate);

```

其实就是把onChange: onCollectValidate 这样的校验触发逻辑混入inputProps，关于表单校验的逻辑其实是用了heyiming大大写的async-validator这个库，使用非常广泛，有空的话也可以深入研究一下，可以另开一篇了~

接下来就是合并新的meta对象，并且存入fieldsStore中对应的name存储空间。
```js
const meta = {
   ...fieldMeta, // 初始化不存在
   ...fieldOption, // 外部传入和内部默认合并后的options
   validate: validateRules, // 上文已经给出示例中结果
};
this.fieldsStore.setFieldMeta(name, meta);
```

setFieldMeta实现就是一个简单的赋值，这样fieldStore内部name这个key就可以读取到存储的数据了。
```js
 setFieldMeta(name, meta) {
    this.fieldsMeta[name] = meta;
  }
```

最后返回inputProps对象 混入input组件，
```js
 return inputProps;

//大概的格式是 
{
   name: 'required',
   onChange(){}, 
   rules: [{required: true}],
}
```

示例中的onSubmit函数调用了validateFields,
抛开表单校验的逻辑不看，可以看到这个方法内部这句。
```js
if (callback) {
   callback(null, this.fieldsStore.getFieldsValue(fieldNames));
}
```
最终整合成{
   key: value
}
这样的结果给外部做表单提交。