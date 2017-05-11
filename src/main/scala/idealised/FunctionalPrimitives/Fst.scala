package idealised.FunctionalPrimitives

import idealised.Compiling.RewriteToImperative
import idealised.Core.OperationalSemantics._
import idealised.Core._
import idealised.DSL.typed._
import idealised.IntermediatePrimitives.MapI
import idealised._

import scala.xml.Elem

final case class Fst(dt1: DataType,
                     dt2: DataType,
                     record: Phrase[ExpType])
  extends ExpPrimitive {

  override lazy val `type` = exp"[$dt1]"

  override def typeCheck(): Unit = {
    import TypeChecker._
    (dt1: DataType) -> (dt2: DataType) ->
      (record :: exp"[$dt1 x $dt2]") -> `type`
  }

  override def inferTypes: Fst = {
    import TypeInference._
    val record_ = TypeInference(record)
    record_.t match {
      case ExpType(RecordType(dt1_, dt2_)) => Fst(dt1_, dt2_, record_)
      case x => error(x.toString, "ExpType(RecordType)")
    }
  }

  override def eval(s: Store): Data = {
    OperationalSemantics.eval(s, record) match {
      case r: RecordData => r.fst
      case _ => throw new Exception("This should not happen")
    }
  }

  override def visitAndRebuild(fun: VisitAndRebuild.Visitor): Phrase[ExpType] = {
    Fst(fun(dt1), fun(dt2), VisitAndRebuild(record, fun))
  }

  override def prettyPrint: String = s"${PrettyPhrasePrinter(record)}._1"

  override def xmlPrinter: Elem =
    <fst dt1={ToString(dt1)} dt2={ToString(dt2)}>
      {Core.xmlPrinter(record)}
    </fst>

  override def rewriteToImperativeAcc(A: Phrase[AccType]): Phrase[CommandType] = {
    import RewriteToImperative._
    con(record)(λ(exp"[$dt1 x $dt2]")(e =>
      dt1 match {
        case b: BasicType => A `:=` Fst(dt1, dt2, e)
        case ArrayType(n, dt) =>
          MapI(n, dt, dt, λ(ExpType(dt))(e => λ(AccType(dt))(a => acc(e)(a))), Fst(dt1, dt2, e), A)
        case RecordType(dt11, dt12) =>
          acc(fst(Fst(dt1, dt2, e)))(recordAcc1(dt11, dt12, A)) `;`
            acc(snd(Fst(dt1, dt2, e)))(recordAcc2(dt11, dt12, A))
        case _: DataTypeIdentifier => throw new Exception("This should not happen")
      }
    ))
  }

  override def rewriteToImperativeCon(C: Phrase[ExpType -> CommandType]): Phrase[CommandType] =
    RewriteToImperative.con(record)(λ(exp"[$dt1 x $dt2]")(e =>
      C(Fst(dt1, dt2, e))
    ))
}
