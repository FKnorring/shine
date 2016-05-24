package ExpPatterns

import Core._
import Core.OperationalSemantics._

case class Fst(record: Phrase[ExpType]) extends ExpPattern {

  override def typeCheck(): ExpType = {
    TypeChecker(record) match {
      case ExpType(RecordType(fst, snd)) => ExpType(fst)
      case t => TypeChecker.error(t.toString, "Something else")
    }
  }

  override def eval(s: Store): Data = {
    OperationalSemantics.eval(s, record) match {
      case r: RecordData => r.fst
      case _ => throw new Exception("This should not happen")
    }
  }

  override def substitute[T <: PhraseType](phrase: Phrase[T], `for`: Phrase[T]): ExpPattern = {
    Fst(OperationalSemantics.substitute(phrase, `for`, record))
  }

  override def toC = Printer.toC(record) + ".fst"

  override def prettyPrint: String = s"${PrettyPrinter(record)}._1"

}
