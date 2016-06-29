package ExpPatterns

import Core._
import Core.OperationalSemantics._
import Core.PhraseType.->
import DSL._
import Compiling.RewriteToImperative
import apart.arithmetic.ArithExpr
import opencl.generator.OpenCLAST.{Expression, Literal}

import scala.xml.Elem

case class Snd(record: Phrase[ExpType]) extends ExpPattern with ViewExpPattern with GeneratableExpPattern {

  override def typeCheck(): ExpType = {
    TypeChecker(record) match {
      case ExpType(RecordType(fst, snd)) => ExpType(snd)
      case x => TypeChecker.error(x.toString, "Something else")
    }
  }

  override def eval(s: Store): Data = {
    OperationalSemantics.eval(s, record) match {
      case r: RecordData => r.snd
      case _ => throw new Exception("This should not happen")
    }
  }

  override def visitAndRebuild(f: VisitAndRebuild.fun): Phrase[ExpType] = {
    Snd(VisitAndRebuild(record, f))
  }

  override def toOpenCL(env: ToOpenCL.Environment): Expression =
    ToOpenCL.exp(this, env, List(), List(), t.dataType)

  override def toOpenCL(env: ToOpenCL.Environment,
                        arrayAccess: List[(ArithExpr, ArithExpr)],
                        tupleAccess: List[ArithExpr],
                        dt: DataType): Expression = {
    ToOpenCL.exp(record, env, arrayAccess, 2 :: tupleAccess, dt)
  }

  override def xmlPrinter: Elem = <snd>{Core.xmlPrinter(record)}</snd>

  override def prettyPrint: String = s"${PrettyPrinter(record)}._2"

  override def rewriteToImperativeAcc(A: Phrase[AccType]): Phrase[CommandType] = {
    import RewriteToImperative._
    exp(this)(λ(this.t) {
      this.t.dataType match {
        case _: BasicType | _: VectorType => x => A `:=` x
        case _: ArrayType => throw new Exception("This should not happen")
        case _: RecordType => throw new Exception("This should not happen")
      }
    })
  }

  override def rewriteToImperativeExp(C: Phrase[ExpType -> CommandType]): Phrase[CommandType] = C(this)
}
